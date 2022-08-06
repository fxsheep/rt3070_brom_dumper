/*
 */

#include <mcs51/8051.h>

void read(void)
{
	*(unsigned char __xdata *)(0x7014) = *(unsigned char __code *)((*(unsigned short __xdata *)(0x7010)) & 0xffff);
	return;
}
