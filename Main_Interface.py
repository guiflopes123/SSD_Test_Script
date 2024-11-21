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
        self.master.title("SSD NVME Test - HT Micron")
        self.master.geometry("1900x1300")

        self.test_options = self.get_test_scripts()  # Obter os nomes dos arquivos Python de teste
        self.disk_list = self.get_disk_devices()  # Obter a lista de dispositivos NVMe e SATA conectados

        self.selected_test_vars = [tk.IntVar() for _ in range(len(self.test_options))]
        self.disk_checkbuttons = []  # Lista para armazenar as checkbuttons de discos
        self.disk_result_widgets = {}  # Dicionário para armazenar widgets de resultado para cada disco
        # Variável para armazenar o número de série
        self.serial_number_var = tk.StringVar()
        self.print_ok_var = tk.IntVar()  # Variável para o check "Impressão OK"
        self.enable_ai_var = tk.IntVar()
        self.lote_var = tk.StringVar()
        self.qtd_pecas_var = tk.IntVar()
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Selecione Itens de Teste:").place(x=50, y=0)

        # Campo para o operador inserir o nome
        tk.Label(self.master, text="Nome do Operador:").place(x=50, y=250)
        self.operator_name_entry = tk.Entry(self.master)
        self.operator_name_entry.place(x=180, y=250)

        tk.Label(self.master, text="Peças Restantes:").place(x=400, y=250)
        self.qtd_pecas_restantes_val = tk.Label(self.master, textvariable=self.qtd_pecas_var, font=("Arial", 10, "bold"))
        self.qtd_pecas_restantes_val.place(x=520, y=250)

        # Caixas de seleção para cada teste
        for i, test in enumerate(self.test_options):
            tk.Checkbutton(self.master, text=test, variable=self.selected_test_vars[i]).place(x=50, y=30 + (i * 30))

        tk.Label(self.master, text="Selecione os Discos:").place(x=400, y=0)

        # Caixas de seleção para cada disco
        for i, disk in enumerate(self.disk_list):
            var = tk.IntVar()
            chk = tk.Checkbutton(self.master, text=disk, variable=var)
            chk.place(x=400, y=30 + (i * 30))
            self.disk_checkbuttons.append((chk, var))

        # tk.Label(self.master, text="AI Report").place(x=600, y=0)
        # Caixa de seleção para AI
        #tk.Checkbutton(self.master, text="AI Report Enable - 1 Min", variable=self.enable_ai_var).place(x=600, y=30)

        # Frame para entrada de Lote e Quantidade de Peças
        entrada_frame = tk.Frame(self.master)
        entrada_frame.pack(pady=10)

        # Campo de entrada para o Lote
        tk.Label(entrada_frame, text="Nome do Lote:").pack(side=tk.LEFT)
        lote_entry = tk.Entry(entrada_frame, textvariable=self.lote_var)
        lote_entry.pack(side=tk.LEFT, padx=5)

        # Campo de entrada para a Quantidade de Peças
        tk.Label(entrada_frame, text="Quantidade de Peças:").pack(side=tk.LEFT)
        qtd_pecas_entry = tk.Entry(entrada_frame, textvariable=self.qtd_pecas_var)
        qtd_pecas_entry.pack(side=tk.LEFT, padx=5)


        # Botões
        tk.Button(self.master, text="Iniciar Teste", command=self.start_test).place(x=50, y=300)
        tk.Button(self.master, text="Limpar Resultados", command=self.clear_results).place(x=200, y=300)
        tk.Button(self.master, text="SAIR", command=self.master.quit).place(x=400, y=300)
        tk.Button(self.master, text="SCAN Discos - 1 Min", command=self.scan_devices).place(x=600, y=300)
        

        self.results_frame = tk.Frame(self.master)
        self.results_frame.place(x=50, y=350)

        # Adiciona a barra de texto fixa na parte inferior da janela
        self.footer = tk.Label(self.master, text="Dev: Guilherme F. Lopes - guilherme.lopes@htmicron.com.br", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.footer.pack(side=tk.BOTTOM, fill=tk.X)

    def scan_devices(self):
        rescan_cmd = "sudo bash reset_pxi_nvme.sh"
        proc = subprocess.Popen(rescan_cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            encoding='utf-8')
        output, error = proc.communicate()
        if proc.returncode == 0:
            print("OK")
        else:
            messagebox.showerror("Error", f"Rescan command failed: {error}")
        rescan_cmd = "sudo bash reset_sata.sh"
        proc = subprocess.Popen(rescan_cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            encoding='utf-8')
        output, error = proc.communicate()
        if proc.returncode == 0:
            print("OK")
        else:
            messagebox.showerror("Error", f"Rescan command failed: {error}")
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
            self.disk_checkbuttons.append((chk, var))

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
            command = "df / | grep / | awk '{print $1}' | sed 's/[0-9]*$//'"
            system_disk_path = subprocess.check_output(command, shell=True, text=True).strip()
            system_disk = system_disk_path[-3:]
            output = subprocess.check_output(['lsblk', '-d', '-o', 'NAME'], text=True)
            for line in output.split('\n'):
                if line.strip():  # Ignora linhas em branco
                    parts = line.split()
                    disk_name = parts[0]
                    if disk_name.startswith('sd') or disk_name.startswith('nvme'):
                        if disk_name != system_disk:
                            disk_devices.append(disk_name)
        except subprocess.CalledProcessError:
            # Trata o erro se o comando lsblk falhar
            messagebox.showerror("Error lsblk.")
            print("Error lsblk.")
        return disk_devices

    def update_print_ok_status(self, var, lbl):
        if var.get() == 1:
            lbl.config(text="OK", fg="green")
        else:
            lbl.config(text="")

    def start_test(self):

        operator_name = self.operator_name_entry.get().strip()
        lote = self.lote_var.get().strip()
        qtd_pecas = self.qtd_pecas_var.get()


        if not lote:
            messagebox.showerror("Error", "Inserir nome do lote")
            return
        
        if not qtd_pecas or qtd_pecas<1:
            messagebox.showerror("Error", "Quantidade do lote.")
            return

        if not operator_name:
            messagebox.showerror("Error", "Inserir nome do operador.")
            return

        selected_tests = [self.test_options[i] for i, var in enumerate(self.selected_test_vars) if var.get() == 1]
        selected_disks = [chk.cget('text') for chk, var in self.disk_checkbuttons if var.get() == 1]

        if not selected_tests:
            messagebox.showerror("Error", "Selecione o teste.")
            return

        if not selected_disks:
            messagebox.showerror("Error", "Selecione o disco.")
            return

        # Limpar widgets de resultado anteriores
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        self.disk_result_widgets = {}

        for i, disk in enumerate(selected_disks):
            disk_frame = tk.Frame(self.results_frame, relief=tk.SUNKEN, borderwidth=1)
            disk_frame.pack(fill=tk.X, pady=5)

            result_label = tk.Label(disk_frame, text=disk, width=20)
            result_label.pack(side=tk.LEFT)

            result_text = tk.Text(disk_frame, height=5, width=80)
            result_text.pack(side=tk.LEFT, padx=5)

            status_label = tk.Label(disk_frame, text="Aguardando", width=10, bg="yellow")
            status_label.pack(side=tk.LEFT, padx=5)

            serial_frame = tk.Frame(disk_frame)
            serial_frame.pack(side=tk.LEFT, padx=(10, 0))

            # Label "Serial Number:"
            serial_label = tk.Label(serial_frame, text="Serial Number:", width=15)
            serial_label.pack()

            # Label para exibir o número de série, logo abaixo do texto
            serial_number_display = tk.Label(serial_frame, text="SN_123456", font=("Arial", 12, "bold"), fg="blue", width=20)
            serial_number_display.pack()

            # Frame de impressão (para o checkbox "Impressão OK" e status)
            print_frame = tk.Frame(disk_frame)
            print_frame.pack(side=tk.LEFT, padx=(10, 0))

            # Variável IntVar para o checkbox de cada disco
            print_ok_var = tk.IntVar()

            # Label para mostrar o status "OK" ao lado do checkbox, deve ser criada aqui para ser única para cada disco
            print_ok_status_label = tk.Label(print_frame, text="", font=("Arial", 12))
            print_ok_status_label.pack()

            # Checkbox "Impressão OK" com status visual usando uma função auxiliar
            print_ok_checkbutton = tk.Checkbutton(
                print_frame, 
                text="Etiqueta", 
                variable=print_ok_var, 
                command=lambda var=print_ok_var, lbl=print_ok_status_label: self.update_print_ok_status(var, lbl), 
                width=15
            )
            print_ok_checkbutton.pack()

            # Salvar os widgets relacionados ao disco em `disk_result_widgets`
            self.disk_result_widgets[disk] = (result_text, status_label, serial_number_display, print_ok_var, print_ok_status_label)

            # Passar `serial_number_display` e `print_ok_status_label` para o teste do disco
            self.run_tests_for_disk(disk, selected_tests, result_text, status_label, operator_name, serial_number_display, lote)
            
            self.update_qtd_pecas_restantes()
            

    def run_tests_for_disk(self, disk, selected_tests, result_text, status_label, operator_name, serial_number_display,lote):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_dir = os.path.dirname(__file__)
        log_dir = os.path.join(base_dir, "Log_Device")
        os.makedirs(log_dir, exist_ok=True)
        output_filename = f"{disk}_{current_time}.txt"
        file_name = os.path.join(log_dir, output_filename)

        lote_dir = os.path.join(base_dir, "Log_Lote")
        os.makedirs(lote_dir, exist_ok=True)
        lote_filename = f"{lote}.txt"
        lote_name = os.path.join(lote_dir, lote_filename)
        
        all_tests_passed = True

        with open(file_name, "w") as logfile:
            
            # Escreve o nome do operador na primeira linha do log
            logfile.write(f"Operator Name: {operator_name}\n")
            logfile.write(f"Nome do lote: {lote}\n")
            logfile.write(f"Test Start Time: {current_time}\n\n")

            for test in selected_tests:
                command = f"sudo python3 Test_Scripts/{test}.py {disk}"
                #result_text.insert(tk.END, f"Executing Test Item: {test} for disk {disk}\n")
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
                            elif match == "FAIL":
                                test_passed = False
                                all_tests_passed = False
                    else:
                        messagebox.showerror("Error", "Test result not found in output.")
                        test_passed = False
                        all_tests_passed = False

                    if test_passed:
                        result_text.insert(tk.END, f"Disk: {disk}, Test Item: {test}, Test Result: PASS\n")
                        logfile.write(f"Disk: {disk}, Test Item: {test}, Test Result: PASS\n")
                    else:
                        result_text.insert(tk.END, f"Disk: {disk}, Test Item: {test}, Test Result: FAIL\n")
                        logfile.write(f"Disk: {disk}, Test Item: {test}, Test Result: FAIL\n")
                
                    lines = result.splitlines()
                    for line in lines:
                        if line.startswith("sn"):
                            split = line.split()
                            sn_name = split[2]     
                            # Atualiza o display com o número de série formatado
                            serial_number_display.config(text=sn_name, font=("Arial", 15, "bold"), fg="blue")

                            # Salva o número de série no arquivo lote_name.txt
                           
                            with open(lote_name, "a") as file:
                                file.write(f"{sn_name}\n")
                            break


                        elif line.startswith("	Serial Number:"):
                            split = line.split()
                            sn_name = split[2]     
                            # Atualiza o display com o número de série formatado
                            serial_number_display.config(text=sn_name, font=("Arial", 15, "bold"), fg="blue")

                            # Salva o número de série no arquivo Serial_Number.txt
                            filename = f"{lote}.txt"  # Nome do arquivo baseado no lote
                            with open(lote_name, "a") as file:
                                file.write(f"{sn_name}\n")
                            break

                        # if line.startswith("fr"):
                        #     split = line.split()
                        #     fw_name = split[2]     
                        #     result_text.insert(tk.END, f"Firmware Name: {fw_name}\n")
                        #     break
                        # elif line.startswith("	Firmware Revision"):
                        #     split = line.split()
                        #     fw_name = split[2]     
                        #     result_text.insert(tk.END, f"Firmware Name: {fw_name}\n")
                        #     break

                except subprocess.CalledProcessError as e:
                    messagebox.showerror("Error", f"Command failed: {e.output}")
                    result_text.insert(tk.END, f"Command failed: {e.output}\n")
                    all_tests_passed = False

        if all_tests_passed:
            status_label.config(text="PASS", bg="green")
        else:
            status_label.config(text="FAIL", bg="red")

        if self.enable_ai_var.get() == 1:
            command = f"sudo python3 gemini-IA.py {output_filename} {current_time}"
            
            try:
                result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
                result_text.insert(tk.END, f"AI Report for {file_name}:\n")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"AI command failed: {e.output}")
                result_text.insert(tk.END, f"AI command failed: {e.output}\n")
        # else:
        #     result_text.insert(tk.END, "AI disabled.\n")

    def clear_results(self):
        # Limpa todos os widgets de resultado
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.disk_result_widgets = {}

    def update_qtd_pecas_restantes(self):
        current_qtd = self.qtd_pecas_var.get()
    
        if current_qtd > 0:
            # Decrementa a quantidade de peças e atualiza o valor exibido
            self.qtd_pecas_var.set(current_qtd - 1)
        else:
            # Exibe uma mensagem de erro se a quantidade for zero ou negativa
            tk.messagebox.showerror("Erro", "Quantidade de peças inválida")

def main():
    root = tk.Tk()
    app = NVME_Test_GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
