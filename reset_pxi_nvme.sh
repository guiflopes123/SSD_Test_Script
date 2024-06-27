#!/bin/bash

# Função para esperar um determinado número de segundos
wait_seconds() {
  local END_TIME=$(( $(date +%s) + $1 ))
  while [ $(date +%s) -lt $END_TIME ]; do
    : # No loop vazio
  done
}

# Função para remover dispositivos PCIe
remove_pci_device() {
  local DEVICE=$1
  if [ -e "/sys/bus/pci/devices/$DEVICE/remove" ]; then
    echo "Removendo explicitamente o dispositivo PCIe $DEVICE..."
    echo 1 > /sys/bus/pci/devices/$DEVICE/remove
    wait_seconds 1
  else
    echo "Dispositivo $DEVICE não encontrado."
  fi
}

# Função para desvincular o driver PCIe
unbind_pci_driver() {
  local DEVICE=$1
  DRIVER=$(basename $(readlink /sys/bus/pci/devices/$DEVICE/driver))
  if [ -n "$DRIVER" ]; then
    echo "Desvinculando o driver $DRIVER do dispositivo PCIe $DEVICE..."
    echo $DEVICE > /sys/bus/pci/drivers/$DRIVER/unbind
    wait_seconds 1
  else
    echo "Driver não encontrado para o dispositivo $DEVICE."
  fi
}

# Função para rescanear o barramento PCIe
rescan_pci_bus() {
  echo "Rescaneando todos os dispositivos PCIe..."
  echo 1 > /sys/bus/pci/rescan
  wait_seconds 1
}

# Função para rescanear dispositivos de bloco
rescan_block_devices() {
  echo "Rescaneando todos os dispositivos de bloco..."
  for host in /sys/class/scsi_host/host*; do
    echo "- - -" > "$host/scan"
  done
  wait_seconds 1
}

# Desvincular e remover dispositivos no barramento 0000:00:01.X
unbind_pci_driver "0000:00:01.0"
remove_pci_device "0000:00:01.0"
unbind_pci_driver "0000:00:01.1"
remove_pci_device "0000:00:01.1"
unbind_pci_driver "0000:00:01.3"
remove_pci_device "0000:00:01.3"

# Rescanear o barramento PCIe após a remoção
rescan_pci_bus

# Rescanear dispositivos de bloco após o rescan do PCIe
rescan_block_devices

# Listar todos os dispositivos PCIe para verificar a detecção atualizada
echo "Lista de dispositivos PCIe:"
lspci -nn

# Listar todos os dispositivos de bloco para verificar a detecção atualizada
echo "Lista de dispositivos de bloco:"
lsblk

echo "Processo de reset e rescan completo."
