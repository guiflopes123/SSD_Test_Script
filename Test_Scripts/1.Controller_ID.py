import subprocess
import sys

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
    #print(f"Informações do Controlador {controller}:\n")
    if controller.startswith('/dev/nvme'):
        cmd = ['sudo', 'nvme', 'id-ctrl', controller]
        print("---------------Controller ID Test----------------")
    elif controller.startswith('/dev/sd'):
        cmd = ['hdparm', '-I', controller]
    else:
        print("Controlador não suportado.\n")
        return False

    controller_info = subprocess.run(cmd, capture_output=True, text=True)
    if controller_info.returncode == 0:
        print("Test Result: PASS\n")
        print(controller_info.stdout)
        return True
    else:
        print("Test Result: FAIL\n")
        return False

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
# partition_name = "sdb"
    test_passed = test_storage(partition_name)

    