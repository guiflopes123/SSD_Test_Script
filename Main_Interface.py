import tkinter as tk
from tkinter import messagebox
import subprocess
import os

class NVME_Test_GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("NVME Test GUI")

        self.test_options = self.get_test_scripts()  # Obter os nomes dos arquivos Python de teste
        self.disk_list = self.get_disk_devices()  # Obter a lista de dispositivos NVMe e SATA conectados

        self.test_selection_var = tk.StringVar()
        self.test_selection_var.set(self.test_options[0])

        self.selected_disk_vars = [tk.IntVar() for _ in range(len(self.disk_list))]

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Selecione o teste a ser aplicado:").pack()

        # Dropdown para selecionar o teste
        self.test_dropdown = tk.OptionMenu(self.master, self.test_selection_var, *self.test_options)
        self.test_dropdown.pack()

        tk.Label(self.master, text="Selecione os discos a serem testados:").pack()

        # Caixas de seleção para cada disco
        for i, disk in enumerate(self.disk_list):
            tk.Checkbutton(self.master, text=disk, variable=self.selected_disk_vars[i]).pack()

        # Botão para iniciar o teste
        tk.Button(self.master, text="Iniciar Teste", command=self.start_test).pack()

        # Área de resultado
        self.result_text = tk.Text(self.master, height=10, width=50)
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
                    if disk_name.startswith('sda') or disk_name.startswith('nvme'):
                        disk_devices.append(disk_name)
        except subprocess.CalledProcessError:
            # Trata o erro se o comando lsblk falhar
            print("Erro ao executar lsblk.")
        return disk_devices

    def start_test(self):
        selected_test = self.test_selection_var.get()
        selected_disk_devices = [self.disk_list[i] for i, var in enumerate(self.selected_disk_vars) if var.get() == 1]

        if not selected_disk_devices:
            messagebox.showerror("Erro", "Selecione pelo menos um disco para testar.")
            return

        messagebox.showinfo("Iniciando Teste", f"Iniciando {selected_test} nos discos: {', '.join(selected_disk_devices)}")

        # Limpa o texto na área de resultado
        self.result_text.delete(1.0, tk.END)

        for disk in selected_disk_devices:
            # Substitua "python test_script.py" pelo comando real para executar o teste
            command = f"python3 Test_Scripts/{selected_test}.py {disk}"

            try:
                result = subprocess.check_output(command, shell=True, text=True)
                # Adiciona o resultado à área de resultado
                self.result_text.insert(tk.END, f"Resultado para {disk}:\n{result}\n\n")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Erro ao iniciar teste", str(e))


def main():
    root = tk.Tk()
    app = NVME_Test_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()