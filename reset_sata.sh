#!/bin/bash

# Função para esperar alguns segundos
wait_seconds() {
  local SECONDS=$1
  sleep $SECONDS
}

# Função para rescanear o barramento SATA
rescan_sata_bus() {
  echo "Rescaneando todos os dispositivos SATA..."
  echo "- - -" > /sys/class/scsi_host/host0/scan
  wait_seconds 2
}

# Identificar o disco onde o sistema está instalado
SYSTEM_DISK=$(df / | grep / | awk '{print $1}' | sed 's/[0-9]*$//')

# Listar todos os dispositivos SATA
list_sata_disks() {
  echo "Lista de dispositivos SATA conectados:"
  lsblk -d -o NAME,TYPE,SIZE,MODEL | grep 'disk' | grep -v "$SYSTEM_DISK"
}

# Rescanear o barramento SATA
rescan_sata_bus

# Listar os discos SATA conectados, excluindo o disco do sistema
list_sata_disks
