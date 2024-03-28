import subprocess
import sys
import datetime

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

def print_controller_info(controller, logfile):
    logfile.write(f"Informações do Controlador {controller}:\n")
    if controller.startswith('/dev/nvme'):
        cmd = ['nvme', 'id-ctrl', controller]
    elif controller.startswith('/dev/sd'):
        cmd = ['hdparm', '-I', controller]
    else:
        logfile.write("Controlador não suportado.\n")
        return False

    controller_info = subprocess.run(cmd, capture_output=True, text=True)
    if controller_info.returncode == 0:
        logfile.write("Test Result: PASS\n")
        logfile.write(controller_info.stdout)
        return True
    else:
        logfile.write("Test Result: FAIL\n")
        return False

def test_storage(partition_name):
    nvme_controllers, sata_controllers = get_nvme_controllers(partition_name)
    if nvme_controllers or sata_controllers:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f'{partition_name}_{current_time}.txt', 'w') as logfile:
            for controller in nvme_controllers:
                if not print_controller_info(controller, logfile):
                    return False
            for controller in sata_controllers:
                if not print_controller_info(controller, logfile):
                    return False
        return True
    else:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Erro ao passar os argumentos")
        sys.exit(1)
    partition_name = sys.argv[1]
    test_passed = test_storage(partition_name)
    print("PASS." if test_passed else "FAIL.")