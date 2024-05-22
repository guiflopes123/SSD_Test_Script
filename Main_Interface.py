import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import re
import datetime


class NVME_Test_GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("NVME Test GUI")

        self.test_options = self.get_test_scripts()  # Obter os nomes dos arquivos Python de teste
        self.disk_list = self.get_disk_devices()  # Obter a lista de dispositivos NVMe e SATA conectados

        self.selected_test_vars = [tk.IntVar() for _ in range(len(self.test_options))]
        self.selected_disk_vars = [tk.IntVar() for _ in range(len(self.disk_list))]
        self.enable_ai_var = tk.IntVar() 
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Selecione os testes a serem aplicados:").pack()

        # Caixas de seleção para cada teste
        for i, test in enumerate(self.test_options):
            tk.Checkbutton(self.master, text=test, variable=self.selected_test_vars[i]).pack()

        tk.Label(self.master, text="Selecione os discos a serem testados:").pack()
              

        # Caixas de seleção para cada disco
        for i, disk in enumerate(self.disk_list):
            tk.Checkbutton(self.master, text=disk, variable=self.selected_disk_vars[i]).pack()
        
        tk.Label(self.master, text="Selecione se deseja habilitar o AI Report").pack()
        #Caixa de seleção para AI
        tk.Checkbutton(self.master, text="AI Report Enable", variable=self.enable_ai_var).pack()

        # Botão para iniciar o teste
        tk.Button(self.master, text="Iniciar Teste", command=self.start_test).pack()

        # Botão para limpar a área de resultado
        tk.Button(self.master, text="Limpar Resultados", command=self.clear_results).pack()

        # Área de resultado
        self.result_text = tk.Text(self.master, height=10, width=80)
        self.result_text.pack()

        # Botão para finalizar o programa
        tk.Button(self.master, text="Finalizar", command=self.master.quit).pack()

    def get_test_scripts(self):
        test_scripts = []
        test_script_dir = "Test_Scripts"
        for file in os.listdir(test_script_dir):
            if file.endswith(".py"):
                test_scripts.append(os.path.splitext(file)[0])
        return test_scripts

    def get_disk_devices(self):
        disk_devices = []
        try:
            output = subprocess.check_output(['lsblk', '-d', '-o', 'NAME'], text=True)
            for line in output.split('\n'):
                if line.strip():  # Ignora linhas em branco
                    parts = line.split()
                    disk_name = parts[0]
                    if disk_name.startswith('sd') or disk_name.startswith('nvme'):
                        disk_devices.append(disk_name)
        except subprocess.CalledProcessError:
            # Trata o erro se o comando lsblk falhar
            messagebox.showerror("Erro ao executar lsblk.")
            print("Erro ao executar lsblk.")
        return disk_devices

    def start_test(self):
        selected_tests = [self.test_options[i] for i, var in enumerate(self.selected_test_vars) if var.get() == 1]
        selected_disks = [self.disk_list[i] for i, var in enumerate(self.selected_disk_vars) if var.get() == 1]
       

        if not selected_tests:
            messagebox.showerror("Erro", "Selecione pelo menos um teste para executar.")
            return

        if not selected_disks:
            messagebox.showerror("Erro", "Selecione pelo menos um disco para testar.")
            return

        
        for disk in selected_disks:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base_dir = os.path.dirname(__file__)
            log_dir = os.path.join(base_dir, "Log")
            output_filename = f"{disk}_{current_time}.txt"
            file_name = f"{log_dir}/{output_filename}"
            with open(file_name, "w") as logfile:
                for test in selected_tests:
                    # Substitua "python test_script.py" pelo comando real para executar o teste
                    command = f"sudo python3 Test_Scripts/{test}.py {disk}"
                       
                    result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
                    # Adiciona o resultado à área de resultado
                    pattern = r"Test Result: (PASS|FAIL)"
                    # Procura todas as linhas que correspondem ao padrão
                    matches = re.findall(pattern, result)
                    # Se encontrou alguma correspondência
                    if matches:
                        # Itera sobre todas as correspondências
                        for match in matches:
                        # Se o status do teste for PASS, então o teste passou
                            if match == "PASS":
                                test_passed = True
                                break
                            # Se o status do teste for FAIL, então o teste falhou
                            elif match == "FAIL":
                                test_passed = False
                            break
                    else:
                        messagebox.showerror("O status do teste não foi encontrado na saída.")
                        test_passed = False

                    if test_passed:
                        self.result_text.insert(tk.END, f"Disk: {disk}, Test Item: {test}, Test Result: PASS\n")
                        # Escreve o resultado no arquivo de log
                        logfile.write(f"Disk: {disk}, Test Item: {test}, Test Result: PASS\n{result}\n")
                    else:
                        self.result_text.insert(tk.END, f"Disk: {disk}, Test Item: {test}, Test Result: FAIL\n")
                        # Escreve o resultado no arquivo de log
                        logfile.write(f"Disk: {disk}, Test Item: {test}, Test Result: FAIL\n{result}\n")
           
            if self.enable_ai_var.get() == 1:
                command = f"sudo python3 gemini-IA.py {output_filename}"
                result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
                self.result_text.insert(tk.END, "AI habilitado.\n")
            else:
                self.result_text.insert(tk.END, "AI desabilitado.\n")
 
    def clear_results(self):
        # Limpa o texto na área de resultado
        self.result_text.delete(1.0, tk.END)


def main():
    root = tk.Tk()
    app = NVME_Test_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
