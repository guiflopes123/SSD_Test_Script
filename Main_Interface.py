import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import re
import datetime
import time

class NVME_Test_GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("NVME Test HT Micron")
        self.master.geometry("800x600")

        self.test_options = self.get_test_scripts()  # Obter os nomes dos arquivos Python de teste
        self.disk_list = self.get_disk_devices()  # Obter a lista de dispositivos NVMe e SATA conectados

        self.selected_test_vars = [tk.IntVar() for _ in range(len(self.test_options))]
        self.disk_checkbuttons = []  # Lista para armazenar as checkbuttons de discos

        self.enable_ai_var = tk.IntVar()
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Test Itens Select:").place(x=50, y=0)

        # Caixas de seleção para cada teste
        for i, test in enumerate(self.test_options):
            tk.Checkbutton(self.master, text=test, variable=self.selected_test_vars[i]).place(x=50, y=30 + (i * 30))

        tk.Label(self.master, text="Disks Select:").place(x=400, y=0)

        # Caixas de seleção para cada disco
        for i, disk in enumerate(self.disk_list):
            var = tk.IntVar()
            chk = tk.Checkbutton(self.master, text=disk, variable=var)
            chk.place(x=400, y=30 + (i * 30))
            self.disk_checkbuttons.append((disk, var))

        tk.Label(self.master, text="AI Report").place(x=600, y=0)
        # Caixa de seleção para AI
        tk.Checkbutton(self.master, text="AI Report Enable", variable=self.enable_ai_var).place(x=600, y=30)

        # Botão para iniciar o teste
        tk.Button(self.master, text="Start Test", command=self.start_test).place(x=50, y=300)

        # Botão para limpar a área de resultado
        tk.Button(self.master, text="Clean Results", command=self.clear_results).place(x=200, y=300)

        # Área de resultado
        self.result_text = tk.Text(self.master, height=10, width=80)
        self.result_text.place(x=50, y=350)

        # Botão para finalizar o programa
        tk.Button(self.master, text="EXIT", command=self.master.quit).place(x=400, y=300)

        # Botão para scanear novos devices
        tk.Button(self.master, text="SCAN", command=self.scan_devices).place(x=600, y=300)

    def scan_devices(self):
        rescan_cmd = "echo 1 > /sys/bus/pci/rescan"
        proc = subprocess.Popen(rescan_cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                encoding='utf-8')
        time.sleep(5)
        proc.wait()
        self.disk_list = self.get_disk_devices()
        self.update_disk_checkbuttons()

    def update_disk_checkbuttons(self):
        # Remove todos os checkbuttons existentes
        for chk, var in self.disk_checkbuttons:
            chk.destroy()
        self.disk_checkbuttons = []

        # Adiciona novos checkbuttons com a lista atualizada de discos
        for i, disk in enumerate(self.disk_list):
            var = tk.IntVar()
            chk = tk.Checkbutton(self.master, text=disk, variable=var)
            chk.place(x=400, y=30 + (i * 30))
            self.disk_checkbuttons.append((disk, var))

    def get_test_scripts(self):
        test_scripts = []
        test_script_dir = "Test_Scripts"
        for file in os.listdir(test_script_dir):
            if file.endswith(".py"):
                test_scripts.append(os.path.splitext(file)[0])
        return sorted(test_scripts)

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
            messagebox.showerror("Error lsblk.")
            print("Error lsblk.")
        return disk_devices

    def start_test(self):
        selected_tests = [self.test_options[i] for i, var in enumerate(self.selected_test_vars) if var.get() == 1]
        selected_disks = [disk for disk, var in self.disk_checkbuttons if var.get() == 1]

        if not selected_tests:
            messagebox.showerror("Error", "No test selected.")
            return

        if not selected_disks:
            messagebox.showerror("Error", "No disk selected.")
            return

        for disk in selected_disks:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            base_dir = os.path.dirname(__file__)
            log_dir = os.path.join(base_dir, "Log")
            os.makedirs(log_dir, exist_ok=True)
            output_filename = f"{disk}_{current_time}.txt"
            file_name = os.path.join(log_dir, output_filename)
            with open(file_name, "w") as logfile:
                for test in selected_tests:
                    command = f"sudo python3 Test_Scripts/{test}.py {disk}"
                    self.result_text.insert(tk.END, f"Executing Test Item: {test} for disk {disk}\n")
                    try:
                        result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
                        logfile.write(result)
                        logfile.write("\n")
                        pattern = r"Test Result: (PASS|FAIL)"
                        matches = re.findall(pattern, result)
                        if matches:
                            for match in matches:
                                if match == "PASS":
                                    test_passed = True
                                    break
                                elif match == "FAIL":
                                    test_passed = False
                                    break
                        else:
                            messagebox.showerror("Error", "Test result not found in output.")
                            test_passed = False

                        if test_passed:
                            self.result_text.insert(tk.END, f"Disk: {disk}, Test Item: {test}, Test Result: PASS\n")
                            logfile.write(f"Disk: {disk}, Test Item: {test}, Test Result: PASS\n")
                        else:
                            self.result_text.insert(tk.END, f"Disk: {disk}, Test Item: {test}, Test Result: FAIL\n")
                            logfile.write(f"Disk: {disk}, Test Item: {test}, Test Result: FAIL\n")
                    except subprocess.CalledProcessError as e:
                        messagebox.showerror("Error", f"Command failed: {e.output}")
                        self.result_text.insert(tk.END, f"Command failed: {e.output}\n")

            if self.enable_ai_var.get() == 1:
                command = f"sudo python3 gemini-IA.py {output_filename}"
                
                try:
                    result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
                    #self.result_text.insert(tk.END, f"AI Report for {file_name}:\n{result}\n")
                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"AI command failed: {e.output}")
                    self.result_text.insert(tk.END, f"AI command failed: {e.output}\n")
            else:
                self.result_text.insert(tk.END, "AI disabled.\n")

    def clear_results(self):
        # Limpa o texto na área de resultado
        self.result_text.delete(1.0, tk.END)

def main():
    root = tk.Tk()
    app = NVME_Test_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
