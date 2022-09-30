#!/usr/bin/env python3
import sys,usb,hexdump

#USB protocol
USB_TYPE_MASK = (0x03 << 5)
USB_TYPE_STANDARD = (0x00 << 5)
USB_TYPE_CLASS = (0x01 << 5)
USB_TYPE_VENDOR = (0x02 << 5)
USB_TYPE_RESERVED = (0x03 << 5)

USB_RECIP_MASK = 0x1f
USB_RECIP_DEVICE = 0x00
USB_RECIP_INTERFACE = 0x01
USB_RECIP_ENDPOINT = 0x02
USB_RECIP_OTHER = 0x03
USB_RECIP_PORT = 0x04
USB_RECIP_RPIPE = 0x05

USB_DIR_OUT = 0
USB_DIR_IN = 0x80

USB_VENDOR_REQUEST = ( USB_TYPE_VENDOR | USB_RECIP_DEVICE )
USB_VENDOR_REQUEST_IN = ( USB_DIR_IN | USB_VENDOR_REQUEST )
USB_VENDOR_REQUEST_OUT = ( USB_DIR_OUT | USB_VENDOR_REQUEST )

#Ralink protocol
USB_DEVICE_MODE = 1
USB_SINGLE_WRITE = 2
USB_SINGLE_READ = 3
USB_MULTI_WRITE = 6
USB_MULTI_READ = 7
USB_EEPROM_WRITE = 8
USB_EEPROM_READ = 9
USB_LED_CONTROL = 10
USB_RX_CONTROL = 12

#MCU mailbox commands
MCU_SLEEP = 0x30
MCU_WAKEUP = 0x31
MCU_RADIO_OFF = 0x35
MCU_CURRENT = 0x36
MCU_LED = 0x50
MCU_LED_STRENGTH = 0x51
MCU_LED_AG_CONF = 0x52
MCU_LED_ACT_CONF = 0x53
MCU_LED_LED_POLARITY = 0x54
MCU_RADAR = 0x60
MCU_BOOT_SIGNAL = 0x72
MCU_ANT_SELECT = 0X73
MCU_FREQ_OFFSET = 0x74
MCU_BBP_SIGNAL = 0x80
MCU_POWER_SAVE = 0x83
MCU_BAND_SELECT = 0x91

#MCU mailbox token
TOKEN_SLEEP = 1
TOKEN_RADIO_OFF = 2
TOKEN_WAKEUP = 3

dev = usb.core.find(idVendor=0x148f, idProduct=0x3070)
if (dev == None):
    dev = usb.core.find(idVendor=0x148f, idProduct=0x2070)
if (dev == None):
    print("No Ralink device found")
    exit()
if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)
dev.set_configuration()

def rt_xram_read(base, size):
    return dev.ctrl_transfer(USB_VENDOR_REQUEST_IN, USB_MULTI_READ, 0, base, size)

def rt_xram_write(base, data):
    dev.ctrl_transfer(USB_VENDOR_REQUEST_OUT, USB_MULTI_WRITE, 0, base, data)

def rt_xram_readl(addr):
    return int.from_bytes(rt_xram_read(addr, 4), "little")

def rt_xram_writel(addr, val):
    rt_xram_write(addr, val.to_bytes(4, byteorder='little'))

def rt_load_shellcode():
    with open("rt2870read.bin", mode='rb') as code:
        shellcode = code.read()
    rt_xram_write(0x319d, shellcode)

def rt_pmem_readb(addr):
    rt_xram_writel(0x7010, 0x01000000 | (addr & 0xffff))
    rt_xram_writel(0x0404, 0x00000055)
    return rt_xram_readl(0x7014) & 0xff

rt_load_shellcode()

with open("romdump.bin", mode='wb') as romfile:
    rom = [0] * 0x1000
    for x in range(0x1000):
        rom[x] = rt_pmem_readb(x)
    romfile.write(bytes(rom))

