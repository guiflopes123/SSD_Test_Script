import subprocess
import sys
import re

def get_nvme_controllers(partition_name):
    nvme_controllers = []
    sata_controllers = []
    partitions_info = subprocess.run(['lsblk', '-d', '-n', '-o', 'NAME'], capture_output=True, text=True)
    partitions = partitions_info.stdout.splitlines()
    for partition in partitions:
        if partition.startswith(partition_name):
            controller = "/dev/" + partition
            if controller.startswith('/dev/nvme'):
                if controller not in nvme_controllers:
                    nvme_controllers.append(controller)
            elif controller.startswith('/dev/sd'):
                if controller not in sata_controllers:
                    sata_controllers.append(controller)
    return nvme_controllers, sata_controllers

def print_controller_info(controller):
        cmd = ['sudo', 'badblocks', '-sv', controller, '100', '0']
        #print(cmd)
        print("---------------Bad Block Test----------------")
        controller_info = subprocess.run(cmd, capture_output=True, text=True)
        if controller_info.returncode == 0:
            lines = controller_info.stderr.splitlines()
            for line in lines:
                if line.startswith("Passo"):
                    error = line.split(" ")
                    if error[3]=="0":
                        print("Test Result: PASS\n")
                        break
                # Se o status do teste for FAIL, então o teste falhou
                    else:
                        print("Test Result: FAIL\n")
                        break

def test_storage(partition_name):
    nvme_controllers, sata_controllers = get_nvme_controllers(partition_name)
    if nvme_controllers or sata_controllers:
            for controller in nvme_controllers:
                if not print_controller_info(controller):
                    return False
            for controller in sata_controllers:
                if not print_controller_info(controller):
                    return False
            return True
    else:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Erro ao passar os argumentos")
        sys.exit(1)
    
    partition_name = sys.argv[1]
    #partition_name = "nvme0n1"
    test_passed = test_storage(partition_name)
