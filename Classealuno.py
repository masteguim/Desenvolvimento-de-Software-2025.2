class Aluno:
    def __init__(self, nome: str, idade: int, matricula: str):
        self.nome = nome
        self.matricula = matricula
        self._idade = idade  
        self.__nota_secreta = 10  

    def mostrar_dados(self):
        print(f"Nome: {self.nome}, Matrícula: {self.matricula}, Idade: {self._idade}")

    def _aniversario(self):
        self._idade += 1

    def __get_nota_secreta(self):
        return self.__nota_secreta
        
    def mostrar_nota(self):
        return f"Nota secreta: {self.__get_nota_secreta()}"

aluno1 = Aluno("Lucas", 19, "3A")

aluno1.mostrar_dados()

print("Idade (via _idade):", aluno1._idade)

aluno1._aniversario()
print("Nova idade:", aluno1._idade)

print(aluno1.mostrar_nota())

print("Forçando acesso ao privado:", aluno1._Aluno__nota_secreta)
