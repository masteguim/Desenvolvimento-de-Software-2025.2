import itertools
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from tkinter import *
from tkinter import messagebox

class Paciente:
    def __init__(self, nome: str, cpf: str, convenio: Optional[str] = None):
        self.nome = nome
        self.cpf = cpf
        self.convenio = convenio
    def __repr__(self):
        return f"Paciente(nome={self.nome!r}, cpf={self.cpf!r})"

class Medico:
    def __init__(self, nome: str, cpf: str, crm: str, especialidade: str = ""):
        self.nome = nome
        self.cpf = cpf
        self.crm = crm
        self.especialidade = especialidade
        # correção: só anota e inicia como None
        self.perfil_paciente: Optional[Paciente] = None
    def __repr__(self):
        return f"Medico(nome={self.nome!r}, crm={self.crm!r})"

class Consulta:
    def __init__(self, _id: int, paciente: Paciente, medico: Medico,
                 inicio: datetime, fim: datetime, local: str = "Sala 1", obs: str = ""):
        if fim <= inicio:
            raise ValueError("Fim deve ser após o início.")
        self.id = _id
        self.paciente = paciente
        self.medico = medico
        self.inicio = inicio
        self.fim = fim
        self.local = local
        self.obs = obs
    def __repr__(self):
        return f"Consulta(id={self.id}, paciente={self.paciente.nome!r}, medico={self.medico.nome!r})"

def conflita(a_ini: datetime, a_fim: datetime, b_ini: datetime, b_fim: datetime) -> bool:
    return a_ini < b_fim and b_ini < a_fim

class Clinica:
    def __init__(self, nome: str):
        self.nome = nome
        self.pacientes: Dict[str, Paciente] = {}     
        self.medicos: Dict[str, Medico] = {}       
        self.consultas: Dict[int, Consulta] = {}   
        self._ids_por_cpf: Dict[str, List[int]] = {}
        self._ids_por_crm: Dict[str, List[int]] = {}
        self._seq = itertools.count(1)

    def add_paciente(self, p: Paciente):
        if not p.nome or not p.cpf:
            raise ValueError("Nome e CPF obrigatórios")
        if p.cpf in self.pacientes:
            raise ValueError("Paciente já cadastrado")
        self.pacientes[p.cpf] = p
        self._ids_por_cpf.setdefault(p.cpf, [])

    def add_medico(self, m: Medico):
        if not m.nome or not m.cpf or not m.crm:
            raise ValueError("Nome, CPF e CRM obrigatórios.")
        if m.crm in self.medicos:
            raise ValueError("Médico já cadastrado.")
        self.medicos[m.crm] = m
        self._ids_por_crm.setdefault(m.crm, [])

    def vincular_medico_como_paciente(self, crm: str, cpf: str):
        if crm not in self.medicos:
            raise KeyError("CRM não encontrado.")
        if cpf not in self.pacientes:
            raise KeyError("CPF não encontrado.")
        self.medicos[crm].perfil_paciente = self.pacientes[cpf]

    def agendar(self, cpf: str, crm: str, inicio: datetime, dur_min: int,
                local: str = "Sala 1", obs: str = "") -> Consulta:
        if cpf not in self.pacientes:
            raise KeyError("Paciente não encontrado.")
        if crm not in self.medicos:
            raise KeyError("Médico não encontrado.")
        fim = inicio + timedelta(minutes=dur_min)
        for cid in self._ids_por_crm.get(crm, []):
            c = self.consultas[cid]
            if conflita(inicio, fim, c.inicio, c.fim):
                raise ValueError("Conflito na agenda do médico.")
        for cid in self._ids_por_cpf.get(cpf, []):
            c = self.consultas[cid]
            if conflita(inicio, fim, c.inicio, c.fim):
                raise ValueError("Conflito na agenda do paciente.")

        novo_id = next(self._seq)
        cons = Consulta(novo_id, self.pacientes[cpf], self.medicos[crm], inicio, fim, local, obs)
        self.consultas[novo_id] = cons
        self._ids_por_crm[crm].append(novo_id)
        self._ids_por_cpf[cpf].append(novo_id)
        return cons

    def cancelar(self, consulta_id: int):
        c = self.consultas.pop(consulta_id, None)
        if not c:
            raise KeyError("Consulta não encontrada.")
        self._ids_por_crm[c.medico.crm].remove(c.id)
        self._ids_por_cpf[c.paciente.cpf].remove(c.id)

    def listar_consultas(self) -> List[Consulta]:
        return sorted(self.consultas.values(), key=lambda x: (x.inicio, x.medico.crm))

def parse_dt(data_str: str, hora_str: str) -> datetime:
    try:
        d = datetime.strptime(data_str.strip(), "%d/%m/%Y").date()
        t = datetime.strptime(hora_str.strip(), "%H:%M").time()
        return datetime.combine(d, t)
    except ValueError:
        raise ValueError("Use data DD/MM/AAAA e hora HH:MM.")

class App(Tk):   
    def __init__(self, clinica: Clinica):
        super().__init__()
        self.c = clinica
        self.title(f"Clínica (mínima) - {self.c.nome}")
        self.geometry("640x600")

        frm_p = LabelFrame(self, text="Paciente")
        frm_p.pack(fill="x", padx=8, pady=6)
        Label(frm_p, text="Nome").grid(row=0, column=0, sticky="w")
        Label(frm_p, text="CPF").grid(row=0, column=2, sticky="w")
        Label(frm_p, text="Convênio").grid(row=1, column=0, sticky="w")
        self.p_nome = Entry(frm_p, width=24); self.p_nome.grid(row=0, column=1, padx=5, pady=3)
        self.p_cpf  = Entry(frm_p, width=18); self.p_cpf.grid(row=0, column=3, padx=5, pady=3)
        self.p_conv = Entry(frm_p, width=18); self.p_conv.grid(row=1, column=1, padx=5, pady=3)
        Button(frm_p, text="Cadastrar Paciente", command=self._add_paciente).grid(row=2, column=0, columnspan=4, pady=4)

        frm_m = LabelFrame(self, text="Médico")
        frm_m.pack(fill="x", padx=8, pady=6)
        Label(frm_m, text="Nome").grid(row=0, column=0, sticky="w")
        Label(frm_m, text="CPF").grid(row=0, column=2, sticky="w")
        Label(frm_m, text="CRM").grid(row=1, column=0, sticky="w")
        Label(frm_m, text="Especialidade").grid(row=1, column=2, sticky="w")
        self.m_nome = Entry(frm_m, width=24); self.m_nome.grid(row=0, column=1, padx=5, pady=3)
        self.m_cpf  = Entry(frm_m, width=18); self.m_cpf.grid(row=0, column=3, padx=5, pady=3)
        self.m_crm  = Entry(frm_m, width=18); self.m_crm.grid(row=1, column=1, padx=5, pady=3)
        self.m_esp  = Entry(frm_m, width=18); self.m_esp.grid(row=1, column=3, padx=5, pady=3)
        Button(frm_m, text="Cadastrar Médico", command=self._add_medico).grid(row=2, column=0, columnspan=4, pady=4)

        frm_v = LabelFrame(self, text="Vincular Médico → Paciente (agregação)")
        frm_v.pack(fill="x", padx=8, pady=6)
        Label(frm_v, text="CRM").grid(row=0, column=0, sticky="w")
        Label(frm_v, text="CPF").grid(row=0, column=2, sticky="w")
        self.v_crm = Entry(frm_v, width=18); self.v_crm.grid(row=0, column=1, padx=5, pady=3)
        self.v_cpf = Entry(frm_v, width=18); self.v_cpf.grid(row=0, column=3, padx=5, pady=3)
        Button(frm_v, text="Vincular", command=self._vincular).grid(row=0, column=4, padx=6)

        frm_a = LabelFrame(self, text="Agendar Consulta")
        frm_a.pack(fill="x", padx=8, pady=6)
        for i, txt in enumerate(("CPF Paciente", "CRM Médico", "Data (DD/MM/AAAA)", "Hora (HH:MM)", "Duração (min)", "Local")):
            Label(frm_a, text=txt).grid(row=i//2, column=(i%2)*2, sticky="w")
        self.a_cpf  = Entry(frm_a, width=18); self.a_cpf.grid(row=0, column=1, padx=5, pady=3)
        self.a_crm  = Entry(frm_a, width=18); self.a_crm.grid(row=0, column=3, padx=5, pady=3)
        self.a_data = Entry(frm_a, width=12); self.a_data.grid(row=1, column=1, padx=5, pady=3)
        self.a_hora = Entry(frm_a, width=8);  self.a_hora.grid(row=1, column=3, padx=5, pady=3)
        self.a_dur  = Entry(frm_a, width=8);  self.a_dur.grid(row=2, column=1, padx=5, pady=3)
        self.a_loc  = Entry(frm_a, width=18); self.a_loc.grid(row=2, column=3, padx=5, pady=3)
        Button(frm_a, text="Agendar", command=self._agendar).grid(row=3, column=0, columnspan=4, pady=4)

        frm_l = LabelFrame(self, text="Consultas")
        frm_l.pack(fill="both", expand=True, padx=8, pady=6)
        self.lb = Listbox(frm_l, height=12)
        self.lb.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        sb = Scrollbar(frm_l, orient="vertical", command=self.lb.yview)
        sb.pack(side="right", fill="y"); self.lb.config(yscrollcommand=sb.set)

        Button(self, text="Cancelar Selecionada", command=self._cancelar).pack(pady=6)

        try:
            self.c.add_paciente(Paciente("Ana Souza", "111.111.111-11", "Saúde+"))
            self.c.add_paciente(Paciente("Bruno Lima", "222.222.222-22"))
            self.c.add_medico(Medico("Dra. Carla", "333.333.333-33", "CRM-SP-12345", "Clínico"))
            self.c.add_medico(Medico("Dr. Diego", "444.444.444-44", "CRM-SP-67890", "Cardio"))
        except Exception:
            pass

        self._refill()

    def _add_paciente(self):
        try:
            p = Paciente(self.p_nome.get().strip(), self.p_cpf.get().strip(), self.p_conv.get().strip() or None)
            self.c.add_paciente(p)
            messagebox.showinfo("OK", "Paciente cadastrado.")
            self.p_nome.delete(0, END); self.p_cpf.delete(0, END); self.p_conv.delete(0, END)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _add_medico(self):
        try:
            m = Medico(self.m_nome.get().strip(), self.m_cpf.get().strip(), self.m_crm.get().strip(), self.m_esp.get().strip())
            self.c.add_medico(m)
            messagebox.showinfo("OK", "Médico cadastrado.")
            for e in (self.m_nome, self.m_cpf, self.m_crm, self.m_esp): e.delete(0, END)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _vincular(self):
        try:
            self.c.vincular_medico_como_paciente(self.v_crm.get().strip(), self.v_cpf.get().strip())
            messagebox.showinfo("OK", "Vínculo criado (médico agora tem um perfil de paciente).")
            self.v_crm.delete(0, END); self.v_cpf.delete(0, END)
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _agendar(self):
        try:
            cpf = self.a_cpf.get().strip()
            crm = self.a_crm.get().strip()
            inicio = parse_dt(self.a_data.get(), self.a_hora.get())
            dur = int(self.a_dur.get())
            loc = self.a_loc.get().strip() or "Sala 1"
            c = self.c.agendar(cpf, crm, inicio, dur, loc)
            messagebox.showinfo("OK", f"Consulta #{c.id} agendada.")
            for e in (self.a_cpf, self.a_crm, self.a_data, self.a_hora, self.a_dur, self.a_loc): e.delete(0, END)
            self._refill()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _cancelar(self):
        try:
            sel = self.lb.curselection()
            if not sel: raise ValueError("Selecione uma consulta na lista.")
            idx = sel[0]
            item = self.lb.get(idx)
            cid_str = item.split(" | ", 1)[0].replace("#", "")
            cid = int(cid_str)
            self.c.cancelar(cid)
            self._refill()
            messagebox.showinfo("OK", f"Consulta #{cid} cancelada.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _refill(self):
        self.lb.delete(0, END)
        for c in self.c.listar_consultas():
            s = f"#{c.id} | {c.inicio:%d/%m %H:%M}-{c.fim:%H:%M} | {c.medico.nome}({c.medico.crm}) → {c.paciente.nome}({c.paciente.cpf}) @ {c.local}"
            self.lb.insert(END, s)

if __name__ == "__main__":
    app = App(Clinica("Clínica Universitária"))
    app.mainloop()