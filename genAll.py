import sys
import getopt
import math
import numpy as np
import argparse
import random
import Queue
import os

def genData(a,m,d):
	v1 = []
	for k in range(0,a):
		v1.append(random.randrange(-128,127,1) + 1j*random.randrange(-128,127,1))

	#print(v1);

	v2 = []
	for k in range(0,a):
		v2.append(random.randrange(0,2,1))
	
	#print(v2);
	
	v3 = np.dot(v1,v2)
	print(v3)
	
	for i in range(0,m):
		f = open("%s\T_R_%d.data"%(d,i),'w')
		ctr = 0
		
		for j in range(0,a,m*4):
			k = j+(4*i)
			mark = 0
			while(k<j+(4*i)+4 and k<a):
				b = int(v1[k].real)
				if (b<0):
					b = ((abs(b) ^ 0b11111111) + 1) & 0b11111111
				f.write('{0:08b}'.format(b))
				k = k+1
			if (k==a):
				for l in range(k,j+(4*i)+4):
					f.write("00000000")
			if (k>a) :
				f.write("00000000000000000000000000000000")
			f.write("\n")
			ctr = ctr+1
		for j in range(ctr,1023):
			f.write("00000000000000000000000000000000\n")
		if(ctr < 1024):
			f.write("00000000000000000000000000000000")
		f.close()
		f = open("%s\T_I_%d.data"%(d,i),'w')
		ctr = 0
		for j in range(0,a,m*4):
			k = j+(4*i)
			while(k<j+(4*i)+4 and k<a):
				b = int(v1[k].imag)
				if (b<0):
					b = ((abs(b) ^ 0b11111111) + 1) & 0b11111111
				f.write('{0:08b}'.format(b))
				k = k+1
			if (k==a):
				for l in range(k,j+(4*i)+4):
					f.write("00000000")
			if (k>a) :
				f.write("00000000000000000000000000000000")
			f.write("\n")
			ctr = ctr+1
		for j in range(ctr,1023):
			f.write("00000000000000000000000000000000\n")
		if(ctr < 1024):
			f.write("00000000000000000000000000000000")
		f.close()
		f = open("%s\X_%d.data"%(d,i),'w')
		ctr = 0
		for j in range(0,a,m*4):
			k = j+(4*i)
			while(k<j+(4*i)+4 and k<a):
				f.write(str(v2[k]))
				k = k+1
			if (k==a):
				for l in range(k,j+(4*i)+4):
					f.write("0")
			f.write("0000000000000000000000000000\n")
			ctr = ctr+1
		for j in range(ctr,1023):
			f.write("00000000000000000000000000000000\n")
		if(ctr < 1024):
			f.write("00000000000000000000000000000000")
		f.close()
	return v3

def createRAM(type,i,n,a):
	f = open("RAM_%s_%d.vhd"%(type,i),'w')

	f.write("library ieee;\n")
	f.write("use ieee.std_logic_1164.all;\n")
	f.write("use ieee.std_logic_unsigned.all;\n")
	f.write("use std.textio.all;\n")

	f.write("entity RAM_%s_%d is\n"%(type,i))
	f.write("\tport (clk : in std_logic;\n")
	f.write("\t\twea : in std_logic;\n")
	f.write("\t\trea : in std_logic;\n")
	f.write("\t\taddra : in std_logic_vector(9 downto 0);\n")
	f.write("\t\taddrb : in std_logic_vector(9 downto 0);\n")
	f.write("\t\tdia : in std_logic_vector(31 downto 0);\n")
	f.write("\t\tdob : out std_logic_vector(31 downto 0)\n")
	f.write(");\n")		
	f.write("end RAM_%s_%d;\n"%(type,i))

	f.write("architecture Behavioral of RAM_%s_%d is\n"%(type,i))
	f.write("\ttype ram_type is array (0 to 1023) of bit_vector (31 downto 0);\n")
	f.write("\timpure function InitRamFromFile (RamFileName : in string) return ram_type is\n")	
	f.write("\t\tFILE RamFile : text is in RamFileName;\n")	
	f.write("\t\tvariable RamFileLine : line;\n")		
	f.write("\t\tvariable RAM : ram_type;\n")		
	f.write("\tbegin\n")		
	f.write("\t\tfor I in ram_type'range loop\n")	
	f.write("\t\t\treadline (RamFile, RamFileLine);\n")		
	f.write("\t\t\tread (RamFileLine, RAM(I));\n")			
	f.write("\t\tend loop;\n")			
	f.write("\t\treturn RAM;\n")		
	f.write("\tend function;\n\n")		
		
	f.write("signal ram : ram_type:= InitRamFromFile(\"H:/smt_4/scratch/%d_%d/%s_%d.data\");\n"%(n,a,type,i))	
	f.write("attribute block_ram : boolean;\n")	
	f.write("attribute block_ram of ram : signal is TRUE;\n\n")

	f.write("begin\n\n")

	f.write("process (clk)\n")
	f.write("begin\n")
	f.write("\tif (clk'event and clk = '1') then\n")
	f.write("\t\tif (wea = '1') then\n")	
	f.write("\t\t\tram(conv_integer(addra)) <= to_bitvector(dia);\n")		
	f.write("\t\tend if;\n")			
	f.write("\t\tif (rea = '1') then\n")		
	f.write("\t\t\tdob <= to_stdlogicvector(ram(conv_integer(addrb)));\n")		
	f.write("\t\telse\n")			
	f.write("\t\t\tdob <= X\"00000000\";\n")		
	f.write("\t\tend if;\n")			
	f.write("\tend if;\n")		
	f.write("end process;\n\n")	

	f.write("end behavioral;\n")
	f.close()

def genRAM(d):
	f = open("%s\RAM.vhd"%d,'w')

	f.write("library ieee;\n")
	f.write("use ieee.std_logic_1164.all;\n")
	f.write("use ieee.std_logic_unsigned.all;\n")
	f.write("use std.textio.all;\n")

	f.write("entity RAM is\n")
	f.write("\tgeneric (content : string := \"%s\T_R_0.data\");\n"%d)
	f.write("\tport (clk : in std_logic;\n")
	f.write("\t\twea : in std_logic;\n")
	f.write("\t\trea : in std_logic;\n")
	f.write("\t\taddra : in std_logic_vector(9 downto 0);\n")
	f.write("\t\taddrb : in std_logic_vector(9 downto 0);\n")
	f.write("\t\tdia : in std_logic_vector(31 downto 0);\n")
	f.write("\t\tdob : out std_logic_vector(31 downto 0)\n")
	f.write(");\n")		
	f.write("end RAM;\n")

	f.write("architecture Behavioral of RAM is\n")
	f.write("\ttype ram_type is array (0 to 1023) of bit_vector (31 downto 0);\n")
	f.write("\timpure function InitRamFromFile (RamFileName : in string) return ram_type is\n")	
	f.write("\t\tFILE RamFile : text is in RamFileName;\n")	
	f.write("\t\tvariable RamFileLine : line;\n")		
	f.write("\t\tvariable RAM : ram_type;\n")		
	f.write("\tbegin\n")		
	f.write("\t\tfor I in ram_type'range loop\n")	
	f.write("\t\t\treadline (RamFile, RamFileLine);\n")		
	f.write("\t\t\tread (RamFileLine, RAM(I));\n")			
	f.write("\t\tend loop;\n")			
	f.write("\t\treturn RAM;\n")		
	f.write("\tend function;\n\n")		
		
	f.write("signal ram : ram_type:= InitRamFromFile(content);\n")	
	f.write("attribute block_ram : boolean;\n")	
	f.write("attribute block_ram of ram : signal is TRUE;\n\n")

	f.write("begin\n\n")

	f.write("process (clk)\n")
	f.write("begin\n")
	f.write("\tif (clk'event and clk = '1') then\n")
	f.write("\t\tif (wea = '1') then\n")	
	f.write("\t\t\tram(conv_integer(addra)) <= to_bitvector(dia);\n")		
	f.write("\t\tend if;\n")			
	f.write("\t\tif (rea = '1') then\n")		
	f.write("\t\t\tdob <= to_stdlogicvector(ram(conv_integer(addrb)));\n")		
	f.write("\t\telse\n")			
	f.write("\t\t\tdob <= X\"00000000\";\n")		
	f.write("\t\tend if;\n")			
	f.write("\tend if;\n")		
	f.write("end process;\n\n")	

	f.write("end behavioral;\n")
	f.close()

def gen_sim_script(n,a,d):
	f = open("%s\sim_%d_%d.do"%(d,n,a),'w')
	f.write("vlib work\n")
	d = d.replace('\\','/')
	f.write("vcom -explicit  -93 \"%s/circuit.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/u_circuit.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/dsp_adder_5.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/dsp_adder.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/mplx.vhd\"\n"%d)
	#f.write("vcom -explicit  -93 \"%s/reg_48.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/accum.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/counter.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/vec_mul.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/tb_vec_mul.vhd\"\n"%d)
	
	#for i in range(0,n/4):
	#	f.write("vcom -explicit  -93 \"H:/smt_4/scratch/%d_%d/RAM_T_R_%d.vhd\"\n"%(n,a,i))
	#	f.write("vcom -explicit  -93 \"H:/smt_4/scratch/%d_%d/RAM_T_I_%d.vhd\"\n"%(n,a,i))
	#	f.write("vcom -explicit  -93 \"H:/smt_4/scratch/%d_%d/RAM_X_%d.vhd\"\n"%(n,a,i))
	
	f.write("vcom -explicit  -93 \"%s/RAM.vhd\"\n"%d)

	f.write("vsim -lib work -t 1ps tb_vec_mul\n")
	f.write("view wave\n")
	f.write("view source\n")
	f.write("view structure\n")
	f.write("view signals\n")
	f.write("add wave *\n")
	f.write("run 2800 ns\n")
	f.close()

def gen_sim_script_csa(n,a,d):
	f = open("%s\sim_%d_%d.do"%(d,n,a),'w')
	f.write("vlib work\n")
	d = d.replace('\\','/')
	f.write("vcom -explicit  -93 \"%s/circuit.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/u_circuit.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/dsp_adder_5.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/dsp_adder.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/FullAdder.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/csa_2_3.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/CLA.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/CLA4.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/reg_8.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/mplx.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/accum.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/counter.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/vec_mul.vhd\"\n"%d)
	f.write("vcom -explicit  -93 \"%s/tb_vec_mul.vhd\"\n"%d)
	
	f.write("vcom -explicit  -93 \"%s/RAM.vhd\"\n"%d)

	f.write("vsim -lib work -t 1ps tb_vec_mul\n")
	f.write("view wave\n")
	f.write("view source\n")
	f.write("view structure\n")
	f.write("view signals\n")
	f.write("add wave *\n")
	f.write("run 2800 ns\n")
	f.close()	
	
def gen_u_circuit_2(m,d):
	class level:
		def __init__(self,x,y):
			self.dsp = x
			self.ent = y

	levels = []
	i = 0
	c = m
	while(c > 1):
		levels.append(level(int(math.ceil(float(c)/float(10))),c))
		c = int(math.ceil(float(c)/float(2)))
		i = i+1
		
	f = open("%s\u_circuit.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")

	f.write("entity u_circuit is\n")
	f.write("\tPort (\tclk : in  STD_LOGIC;\n")
	f.write("\t\t\trst : in  STD_LOGIC;\n")
	for i in range(0,m):
		f.write("\t\t\tc_%d_s : in  STD_LOGIC_VECTOR (7 downto 0);\n"%i)
	f.write("\t\t\ts : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end u_circuit;\n\n")

	f.write("architecture Behavioral of u_circuit is\n\n")

	f.write("component dsp_adder_5 is\n")
	f.write("\tPort (\tclk : in  STD_LOGIC;\n")
	f.write("\t\t\trst : in STD_LOGIC;\n")
	for i in range(0,10):
		f.write("\t\ts_in_%d : in  STD_LOGIC_VECTOR (7 downto 0);\n"%i)
	for i in range(0,4):
		f.write("\t\ts_out_%d : out  STD_LOGIC_VECTOR (7 downto 0):=(others=>'0');\n"%i)
	f.write("\t\ts_out_4 : out  STD_LOGIC_VECTOR (7 downto 0):=(others=>'0'));\n")
	f.write("end component;\n\n")

	f.write("signal\t");
	for i in range(0, len(levels)-1):
		for j in range(0, int(math.ceil(float(levels[i].ent)/float(2)))):
			f.write("s_%d_%d,"%(i,j))
			if(j%10 == 9):
				f.write("\n\t\t")
			else:
				f.write(" ")
		f.write("\n\t\t")
		
	f.write("s_%d_0: std_logic_vector(7 downto 0);\n\n"%(len(levels)-1))

	f.write("begin\n\n")

	q = Queue.Queue()

	for i in range(0, m):
		q.put("c_%d_s"%i)

	for i in range(0,len(levels)):
		for j in range(0,levels[i].dsp-1):
			f.write("Adder_%d_%d_I: dsp_adder_5 port map(\tclk,\n"%(i,j))
			f.write("\t\t\t\t\t\t\trst,\n")
			for k in range (0,10):
				f.write("\t\t\t\t\t\t\t%s,\n"%q.get())
			for k in range (0,4):
				f.write("\t\t\t\t\t\t\ts_%d_%d,\n"%(i,(j*5+k)))
				q.put("s_%d_%d"%(i,(j*5+k)))
			f.write("\t\t\t\t\t\t\ts_%d_%d);\n\n"%(i,(j*5+4)))
			q.put("s_%d_%d"%(i,(j*5+4)))
		rem = levels[i].ent-10*(levels[i].dsp-1)
		f.write("Adder_%d_%d_I: dsp_adder_5 port map(\tclk,\n"%(i,levels[i].dsp-1))
		f.write("\t\t\t\t\t\t\trst,\n")
		for k in range (0,rem):
				f.write("\t\t\t\t\t\t\t%s,\n"%q.get())
		for k in range (rem,10):
				f.write("\t\t\t\t\t\t\tX\"00\",\n")
		for k in range (0,int(math.ceil(float(rem)/float(2)))-1):
			f.write("\t\t\t\t\t\t\ts_%d_%d,\n"%(i,k+(5*(levels[i].dsp-1))))
			q.put("s_%d_%d"%(i,k+(5*(levels[i].dsp-1))))
		f.write("\t\t\t\t\t\t\ts_%d_%d"%(i,(math.ceil(float(rem)/float(2))-1)+(5*(levels[i].dsp-1))))
		q.put("s_%d_%d"%(i,(math.ceil(float(rem)/float(2))-1)+(5*(levels[i].dsp-1))))
		if(int(math.ceil(float(rem)/float(2))) < 5):
			f.write(",\n")
			for k in range (int(math.ceil(float(rem)/float(2))),4):
				f.write("\t\t\t\t\t\t\topen,\n")
			f.write("\t\t\t\t\t\t\topen);\n\n")
		else:
			f.write("\t\t\t\t\t\t\t);\n\n")
				
	f.write("s <= %s;\n\n"%q.get())
	f.write("end Behavioral;")

	f.close();
	return len(levels)
	
def gen_u_circuit(m,d):
	class level:
		def __init__(self,x,y):
			self.dsp = x
			self.ent = y

	levels = []
	i = 0
	c = m
	while(c > 1):
		levels.append(level(int(c//10),0))
		r = c%10
		if (levels[i].dsp==0):
			levels[i].ent = r
			c = int(math.ceil(float(r)/float(2)))
		else:
			c = levels[i].dsp*5+r
		i = i+1
		
	f = open("%s\u_circuit.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")

	f.write("entity u_circuit is\n")
	f.write("\tPort (\tclk : in  STD_LOGIC;\n")
	f.write("\t\t\trst : in  STD_LOGIC;\n")
	for i in range(0,m):
		f.write("\t\t\tc_%d_s : in  STD_LOGIC_VECTOR (7 downto 0);\n"%i)
	f.write("\t\t\ts : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end u_circuit;\n\n")

	f.write("architecture Behavioral of u_circuit is\n\n")

	f.write("component dsp_adder_5 is\n")
	f.write("\tPort (\tclk : in  STD_LOGIC;\n")
	f.write("\t\t\trst : in STD_LOGIC;\n")
	for i in range(0,10):
		f.write("\t\ts_in_%d : in  STD_LOGIC_VECTOR (7 downto 0);\n"%i)
	for i in range(0,4):
		f.write("\t\ts_out_%d : out  STD_LOGIC_VECTOR (7 downto 0):=(others=>'0');\n"%i)
	f.write("\t\ts_out_4 : out  STD_LOGIC_VECTOR (7 downto 0):=(others=>'0'));\n")
	f.write("end component;\n\n")

	f.write("signal\t");
	for i in range(0, len(levels)-1):
		if(levels[i].dsp>0):
			for j in range(0, levels[i].dsp*5):
				f.write("s_%d_%d,"%(i,j))
				if(j%10 == 9):
					f.write("\n\t\t")
				else:
					f.write(" ")
			f.write("\n\t\t")
		else:
			for j in range(0, int(math.ceil(float(levels[i].ent)/float(2)))):
				f.write("s_%d_%d,"%(i,j))
				if(j%10 == 9):
					f.write("\n\t\t")
				else:
					f.write(" ")
			f.write("\n\t\t")
	f.write("s_%d_0: std_logic_vector(7 downto 0);\n\n"%(len(levels)-1))

	f.write("begin\n\n")

	q = Queue.Queue()

	for i in range(0, m):
		q.put("c_%d_s"%i)

	for i in range(0,len(levels)):
		if(levels[i].dsp>0):
			for j in range(0,levels[i].dsp):
				f.write("Adder_%d_%d_I: dsp_adder_5 port map(\tclk,\n"%(i,j))
				f.write("\t\t\t\t\t\t\trst,\n")
				for k in range (0,10):
					f.write("\t\t\t\t\t\t\t%s,\n"%q.get())
				for k in range (0,4):
					f.write("\t\t\t\t\t\t\ts_%d_%d,\n"%(i,(j*5+k)))
					q.put("s_%d_%d"%(i,(j*5+k)))
				f.write("\t\t\t\t\t\t\ts_%d_%d);\n\n"%(i,(j*5+4)))
				q.put("s_%d_%d"%(i,(j*5+4)))
		else:
			f.write("Adder_%d_%d_I: dsp_adder_5 port map(\tclk,\n"%(i,0))
			f.write("\t\t\t\t\t\t\trst,\n")
			for k in range (0,levels[i].ent):
				f.write("\t\t\t\t\t\t\t%s,\n"%q.get())
			for k in range (levels[i].ent,10):
				f.write("\t\t\t\t\t\t\tX\"00\",\n")
			for k in range (0,int(math.ceil(float(levels[i].ent)/float(2)))-1):
				f.write("\t\t\t\t\t\t\ts_%d_%d,\n"%(i,k))
				q.put("s_%d_%d"%(i,k))
			f.write("\t\t\t\t\t\t\ts_%d_%d"%(i,math.ceil(float(levels[i].ent)/float(2))-1))
			q.put("s_%d_%d"%(i,math.ceil(float(levels[i].ent)/float(2))-1))
			if(int(math.ceil(float(levels[i].ent)/float(2))) < 5):
				f.write(",\n")
				for k in range (int(math.ceil(float(levels[i].ent)/float(2))),4):
					f.write("\t\t\t\t\t\t\topen,\n")
				f.write("\t\t\t\t\t\t\topen);\n\n")
			else:
				f.write("\t\t\t\t\t\t\t);\n\n")

	f.write("s <= %s;\n\n"%q.get())
	f.write("end Behavioral;")

	f.close();

def gen_u_circuit_csa(m, r, d):
	class level:
		def __init__(self,x,y,z):
			self.csa = x
			self.cla1 = y
			self.cla2 = z
	
	f = open("%s\u_circuit.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")

	f.write("entity u_circuit is\n")
	f.write("\tPort (\tclk : in  STD_LOGIC;\n")
	f.write("\t\t\trst : in  STD_LOGIC;\n")
	for i in range(0,m):
		f.write("\t\t\tc_%d_s : in  STD_LOGIC_VECTOR (7 downto 0);\n"%i)
	f.write("\t\t\ts : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end u_circuit;\n\n")

	f.write("architecture Behavioral of u_circuit is\n\n")
	
	f.write("component CLA is\n")
	f.write("\tPort (\ta : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\tb : in  STD_LOGIC_VECTOR (7 downto 0);\n")    
	f.write("\t\t\ts : out  STD_LOGIC_VECTOR (7 downto 0);\n")           
	f.write("\t\t\tc_out : out  STD_LOGIC);\n")           
	f.write("end component;\n\n")           

	f.write("component csa_2_3 is\n")
	f.write("\tPort (\tx : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\ty : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\tz : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\ts : out  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\tc : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end component;\n\n")

	f.write("component reg_8 is\n") 
	f.write("\tPort(\tclk : STD_LOGIC;\n")
	f.write("\t\t\trst : in  STD_LOGIC;\n")
	f.write("\t\t\tdata_in : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\tdata_out : out  STD_LOGIC_VECTOR (7 downto 0));\n")  
	f.write("end component;\n\n")
	
	levels = []
	i = 0
	c = m
	while(c > 2):
		levels.append(level(c//3,0,0))
		if (c%3==2):
			levels[i].cla1 = 1
			c = (levels[i].csa)*2 + 1
		elif (c%3==1):
			levels[i].cla2 = 1
			c = (levels[i].csa)*2 + 1
		else:
			c = (levels[i].csa)*2
		i = i+1
	levels.append(level(0,1,0))
	
	f.write("signal\t");
	for i in range(0, len(levels)-1):
		for j in range(0, levels[i].csa + levels[i].cla1 + levels[i].cla2):
			f.write("s_%d_%d,"%(i,j))
			if(j%10 == 9):
				f.write("\n\t\t")
			else:
				f.write(" ")
		f.write("\n\t\t")
	f.write("s_%d_0: std_logic_vector(7 downto 0);\n\n"%(len(levels)-1))
	
	for i in range(0, len(levels)):
		if((i+1) % r==0):
			f.write("signal\t");
			for j in range(0, levels[i].csa + levels[i].cla1 + levels[i].cla2 - 1):
				f.write("s_reg_%d_%d,"%(i,j))
				if(j%10 == 9):
					f.write("\n\t\t")
				else:
					f.write(" ")
			f.write("s_reg_%d_%d: std_logic_vector(7 downto 0);\n"%(i,(levels[i].csa + levels[i].cla1 + levels[i].cla2 - 1)))
	
	if (levels[0].csa != 0):
		f.write("signal\t");
		for i in range(0, len(levels)-2):
			for j in range(0, levels[i].csa):
				f.write("c_%d_%d,"%(i,j))
				if(j%10 == 9):
					f.write("\n\t\t")
				else:
					f.write(" ")
			f.write("\n\t\t")
		f.write("c_%d_0: std_logic_vector(7 downto 0);\n\n"%(len(levels)-2))
	
	for i in range(0, len(levels)-1):
		if((i+1) % r == 0):
			f.write("signal\t");
			for j in range(0, levels[i].csa - 1):
				f.write("c_reg_%d_%d,"%(i,j))
				if(j%10 == 9):
					f.write("\n\t\t")
				else:
					f.write(" ")
			f.write("c_reg_%d_%d: std_logic_vector(7 downto 0);\n"%(i,(levels[i].csa - 1)))
	
	f.write("signal\t");
	for i in range(0, len(levels)-1):
		for j in range(0, levels[i].cla1 + levels[i].cla2):
			f.write("c_out_%d_%d,"%(i,j+levels[i].csa))
			if(j%10 == 9):
				f.write("\n\t\t")
			else:
				f.write(" ")
		if(levels[i].cla1 + levels[i].cla2 != 0):
			f.write("\n\t\t")
	f.write("c_out_%d_0: std_logic;\n\n"%(len(levels)-1))
	
	f.write("begin\n\n")
	
	q = Queue.Queue()

	for i in range(0, m):
		q.put("c_%d_s"%i)
	
	for i in range(0,len(levels)):
		if((i+1) % r == 0):
			for j in range(0,levels[i].csa):
				f.write("CSA_%d_%d_I: csa_2_3 port map(\t%s,\n"%(i,j,q.get()))
				f.write("\t\t\t\t\t\t\t%s,\n"%q.get())
				f.write("\t\t\t\t\t\t\t%s,\n"%q.get())
				f.write("\t\t\t\t\t\t\ts_reg_%d_%d,\n"%(i,j))
				f.write("\t\t\t\t\t\t\tc_reg_%d_%d);\n\n"%(i,j))
				f.write("reg_8_s_%d_%d: reg_8 port map(\tclk,\n"%(i,j))
				f.write("\t\t\t\t\t\t\trst,\n")
				f.write("\t\t\t\t\t\t\ts_reg_%d_%d,\n"%(i,j))
				f.write("\t\t\t\t\t\t\ts_%d_%d);\n\n"%(i,j))
				q.put("s_%d_%d"%(i,j))
				f.write("reg_8_c_%d_%d: reg_8 port map(\tclk,\n"%(i,j))
				f.write("\t\t\t\t\t\t\trst,\n")
				f.write("\t\t\t\t\t\t\tc_reg_%d_%d,\n"%(i,j))
				f.write("\t\t\t\t\t\t\tc_%d_%d);\n\n"%(i,j))
				q.put("c_%d_%d"%(i,j))
			for k in range(0,levels[i].cla1):
				f.write("CLA_%d_%d_I: CLA port map(\t%s,\n"%(i,(k+levels[i].csa),q.get()))
				f.write("\t\t\t\t\t\t%s,\n"%q.get())
				f.write("\t\t\t\t\t\ts_reg_%d_%d,\n"%(i,(k+levels[i].csa)))
				f.write("\t\t\t\t\t\tc_out_%d_%d);\n\n"%(i,(k+levels[i].csa)))
				f.write("reg_8_s_%d_%d: reg_8 port map(\tclk,\n"%(i,(k+levels[i].csa)))
				f.write("\t\t\t\t\t\t\trst,\n")
				f.write("\t\t\t\t\t\t\ts_reg_%d_%d,\n"%(i,(k+levels[i].csa)))
				f.write("\t\t\t\t\t\t\ts_%d_%d);\n\n"%(i,(k+levels[i].csa)))
				q.put("s_%d_%d"%(i,(k+levels[i].csa)))
			for k in range(0,levels[i].cla2):
				f.write("CLA_%d_%d_I: CLA port map(\t%s,\n"%(i,(k+levels[i].csa),q.get()))
				f.write("\t\t\t\t\t\tX\"00\",\n")
				f.write("\t\t\t\t\t\ts_reg_%d_%d,\n"%(i,(k+levels[i].csa)))
				f.write("\t\t\t\t\t\tc_out_%d_%d);\n\n"%(i,(k+levels[i].csa)))
				f.write("reg_8_s_%d_%d: reg_8 port map(\tclk,\n"%(i,(k+levels[i].csa)))
				f.write("\t\t\t\t\t\t\trst,\n")
				f.write("\t\t\t\t\t\t\ts_reg_%d_%d,\n"%(i,(k+levels[i].csa)))
				f.write("\t\t\t\t\t\t\ts_%d_%d);\n\n"%(i,(k+levels[i].csa)))
				q.put("s_%d_%d"%(i,(k+levels[i].csa)))
		else:
			for j in range(0,levels[i].csa):
				f.write("CSA_%d_%d_I: csa_2_3 port map(\t%s,\n"%(i,j,q.get()))
				f.write("\t\t\t\t\t\t\t%s,\n"%q.get())
				f.write("\t\t\t\t\t\t\t%s,\n"%q.get())
				f.write("\t\t\t\t\t\t\ts_%d_%d,\n"%(i,j))
				f.write("\t\t\t\t\t\t\tc_%d_%d);\n\n"%(i,j))
				q.put("s_%d_%d"%(i,j))
				q.put("c_%d_%d"%(i,j))
			for k in range(0,levels[i].cla1):
				f.write("CLA_%d_%d_I: CLA port map(\t%s,\n"%(i,(k+levels[i].csa),q.get()))
				f.write("\t\t\t\t\t\t%s,\n"%q.get())
				f.write("\t\t\t\t\t\ts_%d_%d,\n"%(i,(k+levels[i].csa)))
				f.write("\t\t\t\t\t\tc_out_%d_%d);\n\n"%(i,(k+levels[i].csa)))
				q.put("s_%d_%d"%(i,(k+levels[i].csa)))
			for k in range(0,levels[i].cla2):
				f.write("CLA_%d_%d_I: CLA port map(\t%s,\n"%(i,(k+levels[i].csa),q.get()))
				f.write("\t\t\t\t\t\tX\"00\",\n")
				f.write("\t\t\t\t\t\ts_%d_%d,\n"%(i,(k+levels[i].csa)))
				f.write("\t\t\t\t\t\tc_out_%d_%d);\n\n"%(i,(k+levels[i].csa)))
				q.put("s_%d_%d"%(i,(k+levels[i].csa)))
	
	f.write("s <= %s;\n\n"%q.get())
	f.write("end Behavioral;")

	f.close()
	return len(levels)

def gen_top_modul_2(n,a,d):
	f = open("%s/vec_mul.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")

	f.write("entity vec_mul is\n")
	f.write("\tPort ( clk : in  STD_LOGIC;\n")
	f.write("\t\trst : in  STD_LOGIC;\n")    
	f.write("\t\tstart : in STD_LOGIC;\n")           
	f.write("\t\ts_out_r : out  STD_LOGIC_VECTOR (7 downto 0);\n")			  
	f.write("\t\ts_out_i : out  STD_LOGIC_VECTOR (7 downto 0)\n")           
	f.write(");\n")			  
	f.write("end vec_mul;\n\n")

	f.write("architecture Behavioral of vec_mul is\n")

	f.write("COMPONENT counter\n")
	f.write("\tPORT (\n")
	f.write("\t\tclk : IN STD_LOGIC;\n")
	f.write("\t\trst : IN STD_LOGIC;\n")
	f.write("\t\tQ : OUT STD_LOGIC_VECTOR(9 DOWNTO 0)\n")    
	f.write(");\n")    
	f.write("END COMPONENT;\n")			 
	
	f.write("component RAM is\n")
	f.write("\tgeneric (content : string := \"%s\T_R_0.data\");\n"%d)
	f.write("\tPort (\n")
	f.write("\t\tclk : in std_logic;\n")
	f.write("\t\twea : in std_logic;\n")
	f.write("\t\trea : in std_logic;\n")
	f.write("\t\taddra : in std_logic_vector(9 downto 0);\n")
	f.write("\t\taddrb : in std_logic_vector(9 downto 0);\n")
	f.write("\t\tdia : in std_logic_vector(31 downto 0);\n")
	f.write("\t\tdob : out std_logic_vector(31 downto 0)\n")
	f.write(");\n")
	f.write("end component;\n\n")

	f.write("component circuit is\n")
	f.write("\tPort ( clk : in  STD_LOGIC;\n")
	f.write("\t\trst : in  STD_LOGIC;\n")    
	f.write("\t\tt : in  STD_LOGIC_VECTOR (31 downto 0);\n")           
	f.write("\t\tx : in  STD_LOGIC_VECTOR (3 downto 0);\n")			
	f.write("\t\ts : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end component;\n\n")           

	f.write("component u_circuit is\n")
	f.write("\tPort (\tclk : in  STD_LOGIC;\n")
	f.write("\t\t\trst : in  STD_LOGIC;\n")
	for i in range(0,n/4):
		f.write("\t\t\tc_%d_s : in  STD_LOGIC_VECTOR (7 downto 0);\n"%i)
	f.write("\t\t\ts : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end component;\n\n")

	f.write("COMPONENT accum\n")
	f.write("\tPORT (\n")
	f.write("\t\tclk : in std_logic;\n")
	f.write("\t\trst : in std_logic;\n")
	f.write("\t\tD : in std_logic_vector(7 downto 0);\n")    
	f.write("\t\tQ : out std_logic_vector(7 downto 0)\n")
	f.write(");\n")
	f.write("END COMPONENT;\n")	

	f.write("signal ctr: STD_LOGIC_VECTOR(9 downto 0):=(others=>'0');\n")
	f.write("signal wea: std_logic:='0';\n")
	f.write("signal rea: std_logic:= '0';\n")
	f.write("signal addra_s: std_logic_vector(9 downto 0):=(others=>'0');\n")

	for i in range(0,n/4):
		f.write("signal dina_s_r_%d: std_logic_vector(31 downto 0):=(others=>'0');\n"%i)
		f.write("signal doutb_s_r_%d: std_logic_vector(31 downto 0);\n"%i)
		f.write("signal dina_s_i_%d: std_logic_vector(31 downto 0):=(others=>'0');\n"%i)
		f.write("signal doutb_s_i_%d: std_logic_vector(31 downto 0);\n"%i)
		f.write("signal dina_s_x_%d: std_logic_vector(31 downto 0):=(others=>'0');\n"%i)
		f.write("signal doutb_s_x_%d: std_logic_vector(31 downto 0);\n"%i)
		f.write("signal s_r_%d: std_logic_vector (7 downto 0);\n"%i)
		f.write("signal s_i_%d: std_logic_vector (7 downto 0);\n"%i)

	f.write("signal s_r: std_logic_vector (7 downto 0);\n")
	f.write("signal s_i: std_logic_vector (7 downto 0);\n")

	f.write("signal accum_out_r: std_logic_vector(7 downto 0);\n")
	f.write("signal accum_out_i: std_logic_vector(7 downto 0);\n\n")

	f.write("begin\n\n")
	f.write("counter_0 : counter\n")
	f.write("\tPORT MAP (\n")
	f.write("\t\tclk,\n")
	f.write("\t\trst,\n")    
	f.write("\t\tctr\n")    
	f.write(");\n")
	  
	f.write("process(clk,start)\n")
	f.write("begin\n")
	f.write("\tif(rising_edge(clk)) then\n")
	f.write("\t\tif(start='1') then\n")	
	f.write("\t\t\trea <= '1';\n")		
	f.write("\t\telse\n")			
	f.write("\t\t\trea <= '0';\n")		
	f.write("\t\tend if;\n")			
	f.write("\tend if;\n")		
	f.write("end process;\n")	

	for i in range(0,n/4):
		f.write("RAM_T_R_%d : RAM\n"%i)
		f.write("generic map (content => \"%s\T_R_%d.data\")\n"%(d,i))
		f.write("\tport map(	clk,\n")
		f.write("\t\twea,\n")
		f.write("\t\trea,\n")			
		f.write("\t\taddra_s,\n")			
		f.write("\t\tctr,\n")			
		f.write("\t\tdina_s_r_%d,\n"%i)			
		f.write("\t\tdoutb_s_r_%d\n"%i)			
		f.write(");\n\n")
		f.write("RAM_T_I_%d : RAM\n"%i)
		f.write("generic map (content => \"%s\T_I_%d.data\")\n"%(d,i))
		f.write("\tport map(	clk,\n")
		f.write("\t\twea,\n")
		f.write("\t\trea,\n")			
		f.write("\t\taddra_s,\n")			
		f.write("\t\tctr,\n")			
		f.write("\t\tdina_s_i_%d,\n"%i)			
		f.write("\t\tdoutb_s_i_%d\n"%i)			
		f.write(");\n\n")
		f.write("RAM_X_%d : RAM\n"%i)
		f.write("generic map (content => \"%s\X_%d.data\")\n"%(d,i))
		f.write("\tport map(	clk,\n")
		f.write("\t\twea,\n")
		f.write("\t\trea,\n")			
		f.write("\t\taddra_s,\n")			
		f.write("\t\tctr,\n")			
		f.write("\t\tdina_s_x_%d,\n"%i)			
		f.write("\t\tdoutb_s_x_%d\n"%i)			
		f.write(");\n\n")

	for i in range(0,n/4):
		f.write("circuit_r_%d : circuit\n"%i)
		f.write("\tport map(\n")
		f.write("\t\tclk,\n")
		f.write("\t\trst,\n")				
		f.write("\t\tdoutb_s_r_%d,\n"%i)				
		f.write("\t\tdoutb_s_x_%d(31 downto 28),\n"%i)				
		f.write("\t\ts_r_%d\n"%i)				
		f.write(");\n\n")				
		f.write("circuit_i_%d : circuit\n"%i)
		f.write("\tport map(\n")
		f.write("\t\tclk,\n")
		f.write("\t\trst,\n")				
		f.write("\t\tdoutb_s_i_%d,\n"%i)				
		f.write("\t\tdoutb_s_x_%d(31 downto 28),\n"%i)				
		f.write("\t\ts_i_%d\n"%i)				
		f.write(");\n\n")

	f.write("u_circuit_r : u_circuit\n")
	f.write("\tPORT MAP (\n")
	f.write("\t\tclk,\n")
	f.write("\t\trst,\n")
	for i in range(0,n/4):
		f.write("\t\t\ts_r_%d,\n"%i)
	f.write("\t\t\ts_r);\n")

	f.write("u_circuit_i : u_circuit\n")
	f.write("\tPORT MAP (\n")
	f.write("\t\tclk,\n")
	f.write("\t\trst,\n")
	for i in range(0,n/4):
		f.write("\t\t\ts_i_%d,\n"%i)
	f.write("\t\t\ts_i);\n")

	f.write("accum_r : accum\n")
	f.write("\tPORT MAP (\n")
	f.write("\t\tclk,\n")  
	f.write("\t\trst,\n")    
	f.write("\t\ts_r,\n")    
	f.write("\t\taccum_out_r\n")    
	f.write(");\n\n")  

	f.write("accum_i : accum\n")
	f.write("\tPORT MAP (\n")
	f.write("\t\tclk,\n")  
	f.write("\t\trst,\n")    
	f.write("\t\ts_i,\n")    
	f.write("\t\taccum_out_i\n")    
	f.write(");\n\n")
	 
	f.write("s_out_r <= accum_out_r;\n")
	f.write("s_out_i <= accum_out_i;\n\n")  

	f.write("end Behavioral;")
	
	f.close()
	
def gen_top_modul(n):
	f = open("vec_mul.vhd",'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")

	f.write("entity vec_mul is\n")
	f.write("\tPort ( clk : in  STD_LOGIC;\n")
	f.write("\t\trst : in  STD_LOGIC;\n")    
	f.write("\t\tstart : in STD_LOGIC;\n")           
	f.write("\t\ts_out_r : out  STD_LOGIC_VECTOR (7 downto 0);\n")			  
	f.write("\t\ts_out_i : out  STD_LOGIC_VECTOR (7 downto 0)\n")           
	f.write(");\n")			  
	f.write("end vec_mul;\n\n")

	f.write("architecture Behavioral of vec_mul is\n")

	f.write("COMPONENT counter\n")
	f.write("\tPORT (\n")
	f.write("\t\tclk : IN STD_LOGIC;\n")
	f.write("\t\trst : IN STD_LOGIC;\n")
	f.write("\t\tQ : OUT STD_LOGIC_VECTOR(9 DOWNTO 0)\n")    
	f.write(");\n")    
	f.write("END COMPONENT;\n")			 
	
	for i in range(0,n/4):
		f.write("component RAM_T_R_%d is\n"%i)
		f.write("\tPort (\n")
		f.write("\t\tclk : in std_logic;\n")
		f.write("\t\twea : in std_logic;\n")
		f.write("\t\trea : in std_logic;\n")
		f.write("\t\taddra : in std_logic_vector(9 downto 0);\n")
		f.write("\t\taddrb : in std_logic_vector(9 downto 0);\n")
		f.write("\t\tdia : in std_logic_vector(31 downto 0);\n")
		f.write("\t\tdob : out std_logic_vector(31 downto 0)\n")
		f.write(");\n")
		f.write("end component;\n\n")
		f.write("component RAM_T_I_%d is\n"%i)
		f.write("\tPort (\n")
		f.write("\t\tclk : in std_logic;\n")
		f.write("\t\twea : in std_logic;\n")
		f.write("\t\trea : in std_logic;\n")
		f.write("\t\taddra : in std_logic_vector(9 downto 0);\n")
		f.write("\t\taddrb : in std_logic_vector(9 downto 0);\n")
		f.write("\t\tdia : in std_logic_vector(31 downto 0);\n")
		f.write("\t\tdob : out std_logic_vector(31 downto 0)\n")
		f.write(");\n")
		f.write("end component;\n\n")
		f.write("component RAM_X_%d is\n"%i)
		f.write("\tPort (\n")
		f.write("\t\tclk : in std_logic;\n")
		f.write("\t\twea : in std_logic;\n")
		f.write("\t\trea : in std_logic;\n")
		f.write("\t\taddra : in std_logic_vector(9 downto 0);\n")
		f.write("\t\taddrb : in std_logic_vector(9 downto 0);\n")
		f.write("\t\tdia : in std_logic_vector(31 downto 0);\n")
		f.write("\t\tdob : out std_logic_vector(31 downto 0)\n")
		f.write(");\n")
		f.write("end component;\n\n")

	f.write("component circuit is\n")
	f.write("\tPort ( clk : in  STD_LOGIC;\n")
	f.write("\t\trst : in  STD_LOGIC;\n")    
	f.write("\t\tt : in  STD_LOGIC_VECTOR (31 downto 0);\n")           
	f.write("\t\tx : in  STD_LOGIC_VECTOR (3 downto 0);\n")			
	f.write("\t\ts : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end component;\n\n")           

	f.write("component u_circuit is\n")
	f.write("\tPort (\tclk : in  STD_LOGIC;\n")
	f.write("\t\t\trst : in  STD_LOGIC;\n")
	for i in range(0,n/4):
		f.write("\t\t\tc_%d_s : in  STD_LOGIC_VECTOR (7 downto 0);\n"%i)
	f.write("\t\t\ts : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end component;\n\n")

	f.write("COMPONENT accum\n")
	f.write("\tPORT (\n")
	f.write("\t\tclk : in std_logic;\n")
	f.write("\t\trst : in std_logic;\n")
	f.write("\t\tD : in std_logic_vector(7 downto 0);\n")    
	f.write("\t\tQ : out std_logic_vector(7 downto 0)\n")
	f.write(");\n")
	f.write("END COMPONENT;\n")	

	f.write("signal ctr: STD_LOGIC_VECTOR(9 downto 0):=(others=>'0');\n")
	f.write("signal wea: std_logic:='0';\n")
	f.write("signal rea: std_logic:= '0';\n")
	f.write("signal addra_s: std_logic_vector(9 downto 0):=(others=>'0');\n")

	for i in range(0,n/4):
		f.write("signal dina_s_r_%d: std_logic_vector(31 downto 0):=(others=>'0');\n"%i)
		f.write("signal doutb_s_r_%d: std_logic_vector(31 downto 0);\n"%i)
		f.write("signal dina_s_i_%d: std_logic_vector(31 downto 0):=(others=>'0');\n"%i)
		f.write("signal doutb_s_i_%d: std_logic_vector(31 downto 0);\n"%i)
		f.write("signal dina_s_x_%d: std_logic_vector(31 downto 0):=(others=>'0');\n"%i)
		f.write("signal doutb_s_x_%d: std_logic_vector(31 downto 0);\n"%i)
		f.write("signal s_r_%d: std_logic_vector (7 downto 0);\n"%i)
		f.write("signal s_i_%d: std_logic_vector (7 downto 0);\n"%i)

	f.write("signal s_r: std_logic_vector (7 downto 0);\n")
	f.write("signal s_i: std_logic_vector (7 downto 0);\n")

	f.write("signal accum_out_r: std_logic_vector(7 downto 0);\n")
	f.write("signal accum_out_i: std_logic_vector(7 downto 0);\n\n")

	f.write("begin\n\n")
	f.write("counter_0 : counter\n")
	f.write("\tPORT MAP (\n")
	f.write("\t\tclk,\n")
	f.write("\t\trst,\n")    
	f.write("\t\tctr\n")    
	f.write(");\n")
	  
	f.write("process(clk,start)\n")
	f.write("begin\n")
	f.write("\tif(rising_edge(clk)) then\n")
	f.write("\t\tif(start='1') then\n")	
	f.write("\t\t\trea <= '1';\n")		
	f.write("\t\telse\n")			
	f.write("\t\t\trea <= '0';\n")		
	f.write("\t\tend if;\n")			
	f.write("\tend if;\n")		
	f.write("end process;\n")	

	for i in range(0,n/4):
		f.write("RAM_T_R_%d_0 : RAM_T_R_%d\n"%(i,i))
		f.write("\tport map(	clk,\n")
		f.write("\t\twea,\n")
		f.write("\t\trea,\n")			
		f.write("\t\taddra_s,\n")			
		f.write("\t\tctr,\n")			
		f.write("\t\tdina_s_r_%d,\n"%i)			
		f.write("\t\tdoutb_s_r_%d\n"%i)			
		f.write(");\n\n")
		f.write("RAM_T_I_%d_0 : RAM_T_I_%d\n"%(i,i))
		f.write("\tport map(	clk,\n")
		f.write("\t\twea,\n")
		f.write("\t\trea,\n")			
		f.write("\t\taddra_s,\n")			
		f.write("\t\tctr,\n")			
		f.write("\t\tdina_s_i_%d,\n"%i)			
		f.write("\t\tdoutb_s_i_%d\n"%i)			
		f.write(");\n\n")
		f.write("RAM_X_%d_0 : RAM_X_%d\n"%(i,i))
		f.write("\tport map(	clk,\n")
		f.write("\t\twea,\n")
		f.write("\t\trea,\n")			
		f.write("\t\taddra_s,\n")			
		f.write("\t\tctr,\n")			
		f.write("\t\tdina_s_x_%d,\n"%i)			
		f.write("\t\tdoutb_s_x_%d\n"%i)			
		f.write(");\n\n")

	for i in range(0,n/4):
		f.write("circuit_r_%d : circuit\n"%i)
		f.write("\tport map(\n")
		f.write("\t\tclk,\n")
		f.write("\t\trst,\n")				
		f.write("\t\tdoutb_s_r_%d,\n"%i)				
		f.write("\t\tdoutb_s_x_%d(31 downto 28),\n"%i)				
		f.write("\t\ts_r_%d\n"%i)				
		f.write(");\n\n")				
		f.write("circuit_i_%d : circuit\n"%i)
		f.write("\tport map(\n")
		f.write("\t\tclk,\n")
		f.write("\t\trst,\n")				
		f.write("\t\tdoutb_s_i_%d,\n"%i)				
		f.write("\t\tdoutb_s_x_%d(31 downto 28),\n"%i)				
		f.write("\t\ts_i_%d\n"%i)				
		f.write(");\n\n")

	f.write("u_circuit_r : u_circuit\n")
	f.write("\tPORT MAP (\n")
	f.write("\t\tclk,\n")
	f.write("\t\trst,\n")
	for i in range(0,n/4):
		f.write("\t\t\ts_r_%d,\n"%i)
	f.write("\t\t\ts_r);\n")

	f.write("u_circuit_i : u_circuit\n")
	f.write("\tPORT MAP (\n")
	f.write("\t\tclk,\n")
	f.write("\t\trst,\n")
	for i in range(0,n/4):
		f.write("\t\t\ts_i_%d,\n"%i)
	f.write("\t\t\ts_i);\n")

	f.write("accum_r : accum\n")
	f.write("\tPORT MAP (\n")
	f.write("\t\tclk,\n")  
	f.write("\t\trst,\n")    
	f.write("\t\ts_r,\n")    
	f.write("\t\taccum_out_r\n")    
	f.write(");\n\n")  

	f.write("accum_i : accum\n")
	f.write("\tPORT MAP (\n")
	f.write("\t\tclk,\n")  
	f.write("\t\trst,\n")    
	f.write("\t\ts_i,\n")    
	f.write("\t\taccum_out_i\n")    
	f.write(");\n\n")
	 
	f.write("s_out_r <= accum_out_r;\n")
	f.write("s_out_i <= accum_out_i;\n\n")  

	f.write("end Behavioral;")
	f.close()

def gen_accum(d):
	f = open("%s/accum.vhd"%d,'w')
	f.write("library ieee;\n")
	f.write("use ieee.std_logic_1164.all;\n")
	f.write("use ieee.std_logic_unsigned.all;\n")
	f.write("entity accum is\n")
	f.write("\tport (\n")
	f.write("\t\tclk : in std_logic;\n")
	f.write("\t\trst : in std_logic;\n")
	f.write("\t\tD : in std_logic_vector(7 downto 0);\n")
	f.write("\t\tQ : out std_logic_vector(7 downto 0));\n")
	f.write("end accum;\n")
	f.write("architecture Behavioral of accum is\n")
	f.write("signal cnt : std_logic_vector(7 downto 0);\n")
	f.write("begin\n")
	f.write("\tprocess (clk)\n")
	f.write("\tbegin\n")
	f.write("\t\tif rising_edge(clk) then\n")
	f.write("\t\t\tif (rst = '1') then\n")
	f.write("\t\t\t\tcnt <= (others => '0');\n")
	f.write("\t\t\telse\n")
	f.write("\t\t\t\tcnt <= cnt + D;\n")
	f.write("\t\t\tend if;\n")
	f.write("\t\tend if;\n")
	f.write("\tend process;\n")
	f.write("\tQ <= cnt;\n")
	f.write("end Behavioral;\n")
	f.close()
	
def gen_circuit(d):
	f = open("%s/circuit.vhd"%d,'w')
	f.write("library ieee;\n")
	f.write("use ieee.std_logic_1164.all;\n")
	f.write("entity circuit is\n")
	f.write("\tPort ( clk : in  STD_LOGIC;\n")
	f.write("\t\trst : in  STD_LOGIC;\n")
	f.write("\t\tt : in  STD_LOGIC_VECTOR (31 downto 0);\n")
	f.write("\t\tx : in  STD_LOGIC_VECTOR (3 downto 0);\n")
	f.write("\t\ts : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end circuit;\n\n")

	f.write("architecture Behavioral of circuit is\n\n")

	f.write("component mplx is\n")
	f.write("\tPort ( a : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\tb : in  STD_LOGIC;\n")
	f.write("\t\tc : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end component;\n\n")

	f.write("component dsp_adder_5 is\n")
	f.write("\tPort ( clk : in  STD_LOGIC;\n")
	f.write("\t\trst : in STD_LOGIC;\n")
	f.write("\t\ts_in_0 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_1 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_2 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_3 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_4 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_5 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_6 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_7 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_8 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_9 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_out_0 : out  STD_LOGIC_VECTOR (7 downto 0):=(others=>'0');\n")
	f.write("\t\ts_out_1 : out  STD_LOGIC_VECTOR (7 downto 0):=(others=>'0');\n")
	f.write("\t\ts_out_2 : out  STD_LOGIC_VECTOR (7 downto 0):=(others=>'0');\n")
	f.write("\t\ts_out_3 : out  STD_LOGIC_VECTOR (7 downto 0):=(others=>'0');\n")
	f.write("\t\ts_out_4 : out  STD_LOGIC_VECTOR (7 downto 0):=(others=>'0')) ;\n")
	f.write("end component;\n\n")

	f.write("signal a_s_0, a_s_1, a_s_2, a_s_3: std_logic_vector (7 downto 0);\n")
	f.write("signal b_s_0, b_s_1, b_s_2, b_s_3: std_logic;\n")
	f.write("signal c_s_0, c_s_1, c_s_2, c_s_3: std_logic_vector (7 downto 0);\n\n")

	f.write("signal s_0_0, s_0_1, s_1_0: std_logic_vector (7 downto 0);\n\n")

	f.write("begin\n\n")

	f.write("a_s_0 <= t(31 downto 24);\n")
	f.write("b_s_0 <= x(3);\n")
	f.write("mplx_0 : mplx\n")
	f.write("\tport map(	a_s_0,\n")
	f.write("\t\tb_s_0,\n")
	f.write("\t\tc_s_0\n")
	f.write("\t);\n\n")
	
	f.write("a_s_1 <= t(23 downto 16);\n")
	f.write("b_s_1 <= x(2);\n")
	f.write("mplx_1 : mplx\n")
	f.write("\tport map(	a_s_1,\n")
	f.write("\t\tb_s_1,\n")
	f.write("\t\tc_s_1\n")
	f.write("\t);\n\n")

	f.write("a_s_2 <= t(15 downto 8);\n")
	f.write("b_s_2 <= x(1);\n")
	f.write("mplx_2 : mplx\n")
	f.write("\tport map(	a_s_2,\n")
	f.write("\t\tb_s_2,\n")
	f.write("\t\tc_s_2\n")
	f.write("\t);\n\n")

	f.write("a_s_3 <= t(7 downto 0);\n")
	f.write("b_s_3 <= x(0);\n")
	f.write("mplx_3 : mplx\n")
	f.write("\tport map(	a_s_3,\n")
	f.write("\t\tb_s_3,\n")
	f.write("\t\tc_s_3\n")
	f.write("\t);\n\n")


	f.write("dsp_adder_5_r_0 : dsp_adder_5\n")
	f.write("\tport map(	clk,\n")
	f.write("\t\trst,\n")
	f.write("\t\tc_s_0,\n")
	f.write("\t\tc_s_1,\n")
	f.write("\t\tc_s_2,\n")
	f.write("\t\tc_s_3,\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\ts_0_0,\n")
	f.write("\t\ts_0_1,\n")
	f.write("\t\topen,\n")
	f.write("\t\topen,\n")
	f.write("\t\topen\n")
	f.write("\t);\n\n")
	
	f.write("dsp_adder_5_r_1 : dsp_adder_5\n")
	f.write("\tport map(	clk,\n")
	f.write("\t\trst,\n")
	f.write("\t\ts_0_0,\n")
	f.write("\t\ts_0_1,\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\ts_1_0,\n")
	f.write("\t\topen,\n")
	f.write("\t\topen,\n")
	f.write("\t\topen,\n")
	f.write("\t\topen\n")
	f.write("\t);\n\n")
	
	f.write("\ts <= s_1_0;\n\n")

	f.write("end Behavioral;\n")
	f.close()

def gen_circuit_csa(d):
	f = open("%s/circuit.vhd"%d,'w')
	f.write("library ieee;\n")
	f.write("use ieee.std_logic_1164.all;\n")
	f.write("entity circuit is\n")
	f.write("\tPort ( clk : in  STD_LOGIC;\n")
	f.write("\t\trst : in  STD_LOGIC;\n")
	f.write("\t\tt : in  STD_LOGIC_VECTOR (31 downto 0);\n")
	f.write("\t\tx : in  STD_LOGIC_VECTOR (3 downto 0);\n")
	f.write("\t\ts : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end circuit;\n\n")

	f.write("architecture Behavioral of circuit is\n\n")

	f.write("component mplx is\n")
	f.write("\tPort ( a : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\tb : in  STD_LOGIC;\n")
	f.write("\t\tc : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end component;\n\n")
	
	f.write("component CLA is\n")
	f.write("\tPort (\ta : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\tb : in  STD_LOGIC_VECTOR (7 downto 0);\n")    
	f.write("\t\t\ts : out  STD_LOGIC_VECTOR (7 downto 0);\n")           
	f.write("\t\t\tc_out : out  STD_LOGIC);\n")           
	f.write("end component;\n\n")           

	f.write("component csa_2_3 is\n")
	f.write("\tPort (\tx : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\ty : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\tz : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\ts : out  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\tc : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end component;\n\n")

	f.write("component reg_8 is\n") 
	f.write("\tPort(\tclk : STD_LOGIC;\n")
	f.write("\t\t\trst : in  STD_LOGIC;\n")
	f.write("\t\t\tdata_in : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\t\tdata_out : out  STD_LOGIC_VECTOR (7 downto 0));\n")  
	f.write("end component;\n\n")
	
	f.write("signal a_s_0, a_s_1, a_s_2, a_s_3: std_logic_vector (7 downto 0);\n")
	f.write("signal b_s_0, b_s_1, b_s_2, b_s_3: std_logic;\n")
	f.write("signal c_s_0, c_s_1, c_s_2, c_s_3: std_logic_vector (7 downto 0);\n\n")
	
	f.write("signal	s_0_0, s_0_1, s_1_0, s_2_0: std_logic_vector(7 downto 0);\n")

	f.write("signal	s_reg_0_0, s_reg_0_1: std_logic_vector(7 downto 0);\n")
	f.write("signal	s_reg_1_0: std_logic_vector(7 downto 0);\n")
	f.write("signal	s_reg_2_0: std_logic_vector(7 downto 0);\n")
	f.write("signal	c_0_0, c_1_0: std_logic_vector(7 downto 0);\n")

	f.write("signal	c_reg_0_0: std_logic_vector(7 downto 0);\n")
	f.write("signal	c_reg_1_0: std_logic_vector(7 downto 0);\n")
	f.write("signal	c_out_0_1, c_out_2_0: std_logic;\n")

	f.write("begin\n")
	
	f.write("a_s_0 <= t(31 downto 24);\n")
	f.write("b_s_0 <= x(3);\n")
	f.write("mplx_0 : mplx\n")
	f.write("\tport map(	a_s_0,\n")
	f.write("\t\tb_s_0,\n")
	f.write("\t\tc_s_0\n")
	f.write("\t);\n\n")
	
	f.write("a_s_1 <= t(23 downto 16);\n")
	f.write("b_s_1 <= x(2);\n")
	f.write("mplx_1 : mplx\n")
	f.write("\tport map(	a_s_1,\n")
	f.write("\t\tb_s_1,\n")
	f.write("\t\tc_s_1\n")
	f.write("\t);\n\n")

	f.write("a_s_2 <= t(15 downto 8);\n")
	f.write("b_s_2 <= x(1);\n")
	f.write("mplx_2 : mplx\n")
	f.write("\tport map(	a_s_2,\n")
	f.write("\t\tb_s_2,\n")
	f.write("\t\tc_s_2\n")
	f.write("\t);\n\n")

	f.write("a_s_3 <= t(7 downto 0);\n")
	f.write("b_s_3 <= x(0);\n")
	f.write("mplx_3 : mplx\n")
	f.write("\tport map(	a_s_3,\n")
	f.write("\t\tb_s_3,\n")
	f.write("\t\tc_s_3\n")
	f.write("\t);\n\n")
	
	f.write("CSA_0_0_I: csa_2_3 port map(	c_s_0,\n")
	f.write("\t\tc_s_1,\n")
	f.write("\t\tc_s_2,\n")
	f.write("\t\ts_reg_0_0,\n")
	f.write("\t\tc_reg_0_0);\n\n")

	f.write("reg_8_s_0_0: reg_8 port map(	clk,\n")
	f.write("\t\trst,\n")
	f.write("\t\ts_reg_0_0,\n")
	f.write("\t\ts_0_0);\n\n")

	f.write("reg_8_c_0_0: reg_8 port map(	clk,\n")
	f.write("\t\trst,\n")
	f.write("\t\tc_reg_0_0,\n")
	f.write("\t\tc_0_0);\n\n")

	f.write("CLA_0_1_I: CLA port map(	c_s_3,\n")
	f.write("\t\tX\"00\",\n")
	f.write("\t\ts_reg_0_1,\n")
	f.write("\t\tc_out_0_1);\n\n")

	f.write("reg_8_s_0_1: reg_8 port map(	clk,\n")
	f.write("\t\trst,\n")
	f.write("\t\ts_reg_0_1,\n")
	f.write("\t\ts_0_1);\n\n")

	f.write("CSA_1_0_I: csa_2_3 port map(	s_0_0,\n")
	f.write("\t\tc_0_0,\n")
	f.write("\t\ts_0_1,\n")
	f.write("\t\ts_reg_1_0,\n")
	f.write("\t\tc_reg_1_0);\n\n")

	f.write("reg_8_s_1_0: reg_8 port map(	clk,\n")
	f.write("\t\trst,\n")
	f.write("\t\ts_reg_1_0,\n")
	f.write("\t\ts_1_0);\n\n")

	f.write("reg_8_c_1_0: reg_8 port map(	clk,\n")
	f.write("\t\trst,\n")
	f.write("\t\tc_reg_1_0,\n")
	f.write("\t\tc_1_0);\n\n")

	f.write("CLA_2_0_I: CLA port map(	s_1_0,\n")
	f.write("\t\tc_1_0,\n")
	f.write("\t\ts_reg_2_0,\n")
	f.write("\t\tc_out_2_0);\n\n")

	f.write("reg_8_s_2_0: reg_8 port map(	clk,\n")
	f.write("\t\trst,\n")
	f.write("\t\ts_reg_2_0,\n")
	f.write("\t\ts_2_0);\n\n")

	f.write("s <= s_2_0;\n\n")

	f.write("end Behavioral;\n")
	f.close()
	
def gen_counter(d):
	f = open("%s/counter.vhd"%d,'w')
	f.write("library ieee;\n")
	f.write("use ieee.std_logic_1164.all;\n")
	f.write("use ieee.std_logic_unsigned.all;\n")
	f.write("entity counter is\n")
	f.write("\tport (\n")
	f.write("\t\tclk : in std_logic;\n")
	f.write("\t\trst : in std_logic;\n")
	f.write("\t\tQ : out std_logic_vector(9 downto 0));\n")
	f.write("end counter;\n")
	f.write("architecture Behavioral of counter is\n")
	f.write("\t	signal cnt : std_logic_vector(9 downto 0);\n")
	f.write("begin\n")
	f.write("\t	process (clk)\n")
	f.write("\t	begin\n")
	f.write("\t\tif rising_edge(clk) then\n")
	f.write("\t\t\tif (rst = '1') then\n")
	f.write("\t\t\t\tcnt <= (others => '0');\n")
	f.write("\t\t\telse\n")
	f.write("\t\t\t\tcnt <= cnt + \"0000000001\";\n")
	f.write("\t\t\tend if;\n")
	f.write("\t\tend if;\n")
	f.write("\tend process;\n")
	f.write("\tQ <= cnt;\n")
	f.write("end Behavioral;\n")
	f.close()

def gen_dsp_adder(d):
	f = open("%s/dsp_adder.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n")
	 
	f.write("library UNISIM;\n")
	f.write("use UNISIM.VComponents.all;\n\n")
	 
	f.write("entity dsp_adder is\n")
	f.write("\tport (clk     : in std_logic;\n")
	f.write("\t\top_1	  : in std_logic_vector(47 downto 0);\n")
	f.write("\t\top_2	  : in std_logic_vector(47 downto 0);\n")
	f.write("\t\top_3	  : out std_logic_vector(47 downto 0));\n")
	f.write("end dsp_adder;\n\n")
	 
	f.write("architecture Behavioral of dsp_adder is\n\n")
	 
	f.write("\tsignal alumode_s : std_logic_vector(3 downto 0);\n")
	f.write("\tsignal opmode_s  : std_logic_vector(6 downto 0);\n")
	 
	f.write("\tsignal a_s       : std_logic_vector(29 downto 0);\n")
	f.write("\tsignal b_s       : std_logic_vector(17 downto 0);\n")
	f.write("\tsignal c_s       : std_logic_vector(47 downto 0);\n")
	f.write("\tsignal p_s       : std_logic_vector(47 downto 0);\n\n")
	 
	f.write("begin\n\n")
	 
	f.write("\ta_s <= op_1(47 downto 18);\n")
	f.write("\tb_s <= op_1(17 downto 0);\n")
	f.write("\tc_s <= op_2;\n\n")
	 
	f.write("\talumode_s <= \"0000\";\n")
	f.write("\topmode_s <= \"0110011\";\n\n")		
	 
	f.write("\top_3 <= p_s;\n\n")
	 
	f.write("dsp48e1_inst : dsp48e1\n")
	f.write("\tgeneric map (\n")
	f.write("\t\tACASCREG => 1,\n")
	f.write("\t\tADREG => 1,\n")
	f.write("\t\tALUMODEREG => 0,\n")
	f.write("\t\tAREG => 1,\n")
	f.write("\t\tAUTORESET_PATDET => \"NO_RESET\",\n")
	f.write("\t\tA_INPUT => \"DIRECT\",\n")
	f.write("\t\tBCASCREG => 1,\n")
	f.write("\t\tBREG => 1,\n")
	f.write("\t\tB_INPUT => \"DIRECT\",\n")
	f.write("\t\tCARRYINREG => 0,\n")
	f.write("\t\tCARRYINSELREG => 0,\n")
	f.write("\t\tCREG => 1,\n")
	f.write("\t\tDREG => 1,\n")
	f.write("\t\tINMODEREG	=> 0,\n")
	f.write("\t\tMASK => X\"3FFFFFFFFFFF\",\n")
	f.write("\t\tMREG => 0,\n")
	f.write("\t\tOPMODEREG	=> 0,\n")
	f.write("\t\tPATTERN => X\"000000000000\",\n")
	f.write("\t\tPREG => 1,\n")
	f.write("\t\tSEL_MASK => \"MASK\",\n")
	f.write("\t\tSEL_PATTERN => \"PATTERN\",\n")
	f.write("\t\tUSE_DPORT	 => FALSE,\n")
	f.write("\t\tUSE_MULT => \"NONE\",\n")
	f.write("\t\tUSE_PATTERN_DETECT	=> \"NO_PATDET\",\n")
	f.write("\t\tUSE_SIMD => \"ONE48\")\n")
	f.write("\tport map (\n")
	f.write("\t\tACOUT => open,\n")
	f.write("\t\tBCOUT => open,\n")                   
	f.write("\t\tCARRYCASCOUT => open,\n")           
	f.write("\t\tCARRYOUT => open,\n")                 
	f.write("\t\tMULTSIGNOUT => open,\n")             
	f.write("\t\tOVERFLOW => open,\n")                
	f.write("\t\tP => p_s,\n")                       
	f.write("\t\tPATTERNBDETECT => open,\n")         
	f.write("\t\tPATTERNDETECT => open,\n")          
	f.write("\t\tPCOUT => open,\n")                  
	f.write("\t\tUNDERFLOW => open,\n")               
	f.write("\t\tA  => a_s,\n")
	f.write("\t\tACIN  => (others => '0'),\n")
	f.write("\t\tALUMODE => alumode_s,\n")
	f.write("\t\tB => b_s,\n")
	f.write("\t\tBCIN => (others => '0'),\n")
	f.write("\t\tC => c_s,\n")
	f.write("\t\tCARRYCASCIN => '0',\n")
	f.write("\t\tCARRYIN => '0',\n")
	f.write("\t\tCARRYINSEL => (others => '0'),\n")		  
	f.write("\t\tCEA1 => '0',\n")
	f.write("\t\tCEA2  => '1',\n")
	f.write("\t\tCEAD   => '0',\n") 
	f.write("\t\tCEALUMODE   => '0',\n")
	f.write("\t\tCEB1 => '0',\n")
	f.write("\t\tCEB2  => '1',\n")
	f.write("\t\tCEC => '1',\n")
	f.write("\t\tCECARRYIN  => '0',\n")
	f.write("\t\tCECTRL   => '1',\n")
	f.write("\t\tCED  => '0',\n") 
	f.write("\t\tCEINMODE  => '1',\n") 
	f.write("\t\tCEM => '0',\n")
	f.write("\t\tCEP => '1',\n")
	f.write("\t\tCLK => clk,\n")
	f.write("\t\tD => (others => '0'),\n")       
	f.write("\t\tINMODE => (others => '0'),\n")                  
	f.write("\t\tMULTSIGNIN => '0',\n")             
	f.write("\t\tOPMODE => opmode_s,\n")                  
	f.write("\t\tPCIN => (others => '0'),\n")                   
	f.write("\t\tRSTA => '0',\n")
	f.write("\t\tRSTALLCARRYIN  => '0',\n")
	f.write("\t\tRSTALUMODE => '0',\n")
	f.write("\t\tRSTB  => '0',\n")
	f.write("\t\tRSTC  => '0',\n")
	f.write("\t\tRSTCTRL  => '0',\n")
	f.write("\t\tRSTD  => '0',\n")
	f.write("\t\tRSTINMODE  => '0',\n")
	f.write("\t\tRSTM  => '0',\n")
	f.write("\t\tRSTP => '0');\n\n")
	 
	f.write("end Behavioral;\n")
	f.close()

def gen_dsp_adder_5(d):
	f = open("%s/dsp_adder_5.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")
	
	f.write("entity dsp_adder_5 is\n")
	f.write("\tPort ( clk : in  STD_LOGIC;\n")
	f.write("\t\trst : in STD_LOGIC;\n")
	f.write("\t\ts_in_0 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_1 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_2 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_3 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_4 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_5 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_6 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_7 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_8 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_in_9 : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_out_0 : out  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_out_1 : out  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_out_2 : out  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_out_3 : out  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_out_4 : out  STD_LOGIC_VECTOR (7 downto 0)) ;\n")
	f.write("end dsp_adder_5;\n\n")

	f.write("architecture Behavioral of dsp_adder_5 is\n\n")

	f.write("component dsp_adder is\n")
	f.write("\tport (clk     : in std_logic;\n")
	f.write("\t\top_1	  : in std_logic_vector(47 downto 0);\n")
	f.write("\t\top_2	  : in std_logic_vector(47 downto 0);\n")
	f.write("\t\top_3	  : out std_logic_vector(47 downto 0));\n")
	f.write("end component;\n\n")

	f.write("signal op_1_s: std_logic_vector(47 downto 0);\n")
	f.write("signal op_2_s: std_logic_vector(47 downto 0);\n")
	f.write("signal op_1_s_reg: std_logic_vector(47 downto 0);\n")
	f.write("signal op_2_s_reg: std_logic_vector(47 downto 0);\n")
	f.write("signal op_3_s: std_logic_vector(47 downto 0);\n")
	f.write("signal op_3_s_reg: std_logic_vector(47 downto 0);\n\n")

	f.write("begin\n")
	f.write("\top_1_s_reg <= \"0000\" & s_in_0 & '0' & s_in_2 & '0' & s_in_4 & '0' & s_in_6 & '0' & s_in_8;\n")
	f.write("\top_2_s_reg <= \"0000\" & s_in_1 & '0' & s_in_3 & '0' & s_in_5 & '0' & s_in_7 & '0' & s_in_9;\n\n")
	
	f.write("\tdsp_adder_i: dsp_adder \n")
	f.write("\tport map(	clk,\n")
	f.write("\t\top_1_s_reg,\n")
	f.write("\t\top_2_s_reg,\n")
	f.write("\t\top_3_s);\n\n")
	
	f.write("\ts_out_0 <= op_3_s(43 downto 36);\n")
	f.write("\ts_out_1 <= op_3_s(34 downto 27);\n")
	f.write("\ts_out_2 <= op_3_s(25 downto 18);\n")
	f.write("\ts_out_3 <= op_3_s(16 downto 9);\n")
	f.write("\ts_out_4 <= op_3_s(7 downto 0);\n\n")
	
	f.write("end Behavioral;\n")
	
	f.close()

def gen_mplx(d):
	f = open("%s/mplx.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")
	
	f.write("entity mplx is\n")
	f.write("\tPort ( a : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\tb : in  STD_LOGIC;\n")
	f.write("\t\tc : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end mplx;\n\n")

	f.write("architecture Behavioral of mplx is\n\n")

	f.write("begin\n")
	f.write("\tc <= a when b='1' else\n")
	f.write("\t\t\"00000000\";\n\n")
	
	f.write("end Behavioral;")
	f.close()

def gen_full_adder(d):
	f = open("%s/FullAdder.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")
	
	f.write("entity FullAdder is\n")
	f.write("\tPort ( c_in : in  STD_LOGIC;\n")
	f.write("\t\ta : in  STD_LOGIC;\n")
	f.write("\t\tb : in  STD_LOGIC;\n")
	f.write("\t\ts : out  STD_LOGIC;\n")
	f.write("\t\tc_out : out  STD_LOGIC);\n")
	f.write("end FullAdder;\n\n")

	f.write("architecture Behavioral of FullAdder is\n")
	f.write("begin\n")
	f.write("s <= a xor b xor c_in;\n")
	f.write("c_out <= (a and b) or (c_in and (a or b));\n\n")

	f.write("end Behavioral;\n")
	f.close()

def gen_csa_2_3(d):
	f = open("%s/csa_2_3.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")
	
	f.write("entity csa_2_3 is\n")
	f.write("\tPort ( x : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ty : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\tz : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts : out  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\tc : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end csa_2_3;\n\n")

	f.write("architecture Behavioral of csa_2_3 is\n\n")

	f.write("component FullAdder is\n")
	f.write("\tPort ( c_in : in  STD_LOGIC;\n")
	f.write("\t\ta : in  STD_LOGIC;\n")
	f.write("\t\tb : in  STD_LOGIC;\n")
	f.write("\t\ts : out  STD_LOGIC;\n")
	f.write("\t\tc_out : out  STD_LOGIC);\n")
	f.write("end component;\n\n")

	f.write("signal x_0, x_1, x_2, x_3, x_4, x_5, x_6, x_7: STD_LOGIC;\n")
	f.write("signal y_0, y_1, y_2, y_3, y_4, y_5, y_6, y_7: STD_LOGIC;\n")
	f.write("signal z_0, z_1, z_2, z_3, z_4, z_5, z_6, z_7: STD_LOGIC;\n")
	f.write("signal u: STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("signal v: STD_LOGIC_VECTOR (8 downto 0);\n\n")

	f.write("begin\n")

	f.write("v(0) <= '0';\n")
	f.write("z_0 <= z(0);\n")
	f.write("x_0 <= x(0);\n")
	f.write("y_0 <= y(0);\n\n")

	f.write("FA0: FullAdder port map(z_0,\n")
	f.write("\t\tx_0,\n")
	f.write("\t\ty_0,\n")
	f.write("\t\tu(0),\n")
	f.write("\t\tv(1));\n\n")

	f.write("z_1 <= z(1);\n")
	f.write("x_1 <= x(1);\n")
	f.write("y_1 <= y(1);\n\n")

	f.write("FA1: FullAdder port map(z_1,\n")
	f.write("\t\tx_1,\n")
	f.write("\t\ty_1,\n")
	f.write("\t\tu(1),\n")
	f.write("\t\tv(2));\n\n")

	f.write("z_2 <= z(2);\n")
	f.write("x_2 <= x(2);\n")
	f.write("y_2 <= y(2);\n\n")

	f.write("FA2: FullAdder port map(z_2,\n")
	f.write("\t\tx_2,\n")
	f.write("\t\ty_2,\n")
	f.write("\t\tu(2),\n")
	f.write("\t\tv(3));\n\n")

	f.write("z_3 <= z(3);\n")
	f.write("x_3 <= x(3);\n")
	f.write("y_3 <= y(3);\n")

	f.write("FA3: FullAdder port map(z_3,\n")
	f.write("\t\tx_3,\n")
	f.write("\t\ty_3,\n")
	f.write("\t\tu(3),\n")
	f.write("\t\tv(4));\n\n")

	f.write("z_4 <= z(4);\n")
	f.write("x_4 <= x(4);\n")
	f.write("y_4 <= y(4);\n\n")

	f.write("FA4: FullAdder port map(z_4,\n")
	f.write("\t\tx_4,\n")
	f.write("\t\ty_4,\n")
	f.write("\t\tu(4),\n")
	f.write("\t\tv(5));\n\n")

	f.write("z_5 <= z(5);\n")
	f.write("x_5 <= x(5);\n")
	f.write("y_5 <= y(5);\n\n")

	f.write("FA5: FullAdder port map(z_5,\n")
	f.write("\t\tx_5,\n")
	f.write("\t\ty_5,\n")
	f.write("\t\tu(5),\n")
	f.write("\t\tv(6));\n\n")

	f.write("z_6 <= z(6);\n")
	f.write("x_6 <= x(6);\n")
	f.write("y_6 <= y(6);\n")

	f.write("FA6: FullAdder port map(z_6,\n")
	f.write("\t\tx_6,\n")
	f.write("\t\ty_6,\n")
	f.write("\t\tu(6),\n")
	f.write("\t\tv(7));\n\n")

	f.write("z_7 <= z(7);\n")
	f.write("x_7 <= x(7);\n")
	f.write("y_7 <= y(7);\n\n")

	f.write("FA7: FullAdder port map(z_7,\n")
	f.write("\t\tx_7,\n")
	f.write("\t\ty_7,\n")
	f.write("\t\tu(7),\n")
	f.write("\t\tv(8));\n\n")

	f.write("s <= u;\n")
	f.write("c <= v(7 downto 0);\n\n")

	f.write("end Behavioral;\n")
	
	f.close()

def gen_CLA(d):
	f = open("%s/CLA.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")
	
	f.write("entity CLA is\n")
	f.write("\tPort ( a : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\tb : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts : out  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\tc_out : out  STD_LOGIC);\n")
	f.write("end CLA;\n\n")

	f.write("architecture Behavioral of CLA is\n")
	f.write("component CLA4 is\n")
	f.write("\tPort ( a : in  STD_LOGIC_VECTOR (3 downto 0);\n")
	f.write("\t\tb : in  STD_LOGIC_VECTOR (3 downto 0);\n")
	f.write("\t\tc : in  STD_LOGIC;\n")
	f.write("\t\ts : out  STD_LOGIC_VECTOR (3 downto 0);\n")
	f.write("\t\tg : out  STD_LOGIC;\n")
	f.write("\t\tp : out  STD_LOGIC);\n")
	f.write("end component;\n\n")

	f.write("signal a_0, a_1, b_0, b_1, s_0, s_1 : STD_LOGIC_VECTOR (3 downto 0);\n")
	f.write("signal c_0, c_1, g_0, g_1, p_0, p_1 : STD_LOGIC;\n\n")

	f.write("begin\n\n")

	f.write("a_0 <= a(3 downto 0);\n")
	f.write("b_0 <= b(3 downto 0);\n")
	f.write("c_0 <= '0';\n")
	f.write("CLA4_0: CLA4 port map(	a_0,\n")
	f.write("\t\tb_0,\n")
	f.write("\t\tc_0,\n")
	f.write("\t\ts_0,\n")
	f.write("\t\tg_0,\n")
	f.write("\t\tp_0);\n\n")
									
	f.write("a_1 <= a(7 downto 4);\n")
	f.write("b_1 <= b(7 downto 4);\n")
	f.write("c_1 <= g_0 or (c_0 and p_0);\n")
	f.write("CLA4_1: CLA4 port map(	a_1,\n")
	f.write("\t\tb_1,\n")
	f.write("\t\tc_1,\n")
	f.write("\t\ts_1,\n")
	f.write("\t\tg_1,\n")
	f.write("\t\tp_1);\n\n")
	
	f.write("s <= s_1 & s_0;\n")								
	f.write("c_out <= (g_1 or (g_0 and p_1)) or ((c_0 and p_0) and p_1);\n\n")								

	f.write("end Behavioral;\n")
	
	f.close()

def gen_CLA4(d):
	f = open("%s/CLA4.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")
	
	f.write("entity CLA4 is\n")
	f.write("\tPort ( a : in  STD_LOGIC_VECTOR (3 downto 0);\n")
	f.write("\t\tb : in  STD_LOGIC_VECTOR (3 downto 0);\n")
	f.write("\t\tc : in  STD_LOGIC;\n")
	f.write("\t\ts : out  STD_LOGIC_VECTOR (3 downto 0);\n")
	f.write("\t\tg : out  STD_LOGIC;\n")
	f.write("\t\tp : out  STD_LOGIC);\n")
	f.write("end CLA4;\n\n")

	f.write("architecture Behavioral of CLA4 is\n\n")

	f.write("signal g_0, g_1, g_2, g_3 : STD_LOGIC;\n")
	f.write("signal p_0, p_1, p_2, p_3 : STD_LOGIC;\n")
	f.write("signal c_1, c_2, c_3 : STD_LOGIC;\n\n")

	f.write("begin\n\n")

	f.write("g_0 <= a(0) and b(0);\n")
	f.write("g_1 <= a(1) and b(1);\n")
	f.write("g_2 <= a(2) and b(2);\n")
	f.write("g_3 <= a(3) and b(3);\n\n")

	f.write("p_0 <= a(0) or b(0);\n")
	f.write("p_1 <= a(1) or b(1);\n")
	f.write("p_2 <= a(2) or b(2);\n")
	f.write("p_3 <= a(3) or b(3);\n\n")

	f.write("c_1 <= g_0 or (c and p_0);\n")
	f.write("c_2 <= (g_1 or (g_0 and p_1)) or ((c and p_0) and p_1);\n")
	f.write("c_3 <= (g_2 or (g_1 and p_2)) or (((g_0 and p_1) and p_2) or ((c and p_0) and (p_1 and p_2)));\n\n")

	f.write("s <= ((a(3) xor b(3)) xor c_3) & ((a(2) xor b(2)) xor c_2) & ((a(1) xor b(1)) xor c_1) & ((a(0) xor b(0)) xor c);\n")  
	f.write("g <= (g_3 or (g_2 and p_3)) or (((g_1 and p_2) and p_3) or ((g_0 and p_1) and (p_2 and p_3)));\n")
	f.write("p <= (p_0 and p_1) and (p_2 and p_3);\n\n")

	f.write("end Behavioral;\n")
	
	f.close()

def gen_reg_8(d):
	f = open("%s/reg_8.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")
	
	f.write("entity reg_8 is\n")
	f.write("\tPort ( clk : in  STD_LOGIC;\n")
	f.write("\t\trst : in  STD_LOGIC;\n")
	f.write("\t\tdata_in : in  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\tdata_out : out  STD_LOGIC_VECTOR (7 downto 0));\n")
	f.write("end reg_8;\n\n")

	f.write("architecture Behavioral of reg_8 is\n")
	f.write("signal reg_8_s: std_logic_vector(7 downto 0);\n\n")

	f.write("begin\n")
	f.write("\tpr_reg: process(clk,rst)\n")
	f.write("\tbegin\n")
	f.write("\t\tif rising_edge(clk) then\n")
	f.write("\t\t\tif rst = '1' then\n")
	f.write("\t\t\t\treg_8_s <= (others => '0');\n")
	f.write("\t\t\telse\n")
	f.write("\t\t\t\treg_8_s <= data_in;\n")
	f.write("\t\t\tend if;\n")
	f.write("\t\tend if;\n")
	f.write("\tend process;\n\n")
	
	f.write("data_out <= reg_8_s;\n")
	f.write("end Behavioral;\n")
	
	f.close()

def gen_tb(n,a,d,result,l):
	rr = int(result.real)
	ri = int(result.imag)
	if (rr<0):
		rr = ((abs(rr) ^ 0b11111111) + 1) & 0b11111111
	if (ri<0):
		ri = ((abs(ri) ^ 0b11111111) + 1) & 0b11111111
	rr = rr & 0b11111111
	ri = ri & 0b11111111
	t = int(math.ceil(float(a)/float(n)))
	
	f = open("%s/tb_vec_mul.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")
	f.write("ENTITY tb_vec_mul IS\n")
	f.write("END tb_vec_mul;\n\n")
	 
	f.write("ARCHITECTURE behavior OF tb_vec_mul IS\n\n") 
	 
	f.write("COMPONENT vec_mul\n")
	f.write("\tPORT(\n")
	f.write("\t\tclk : in  STD_LOGIC;\n")
	f.write("\t\trst : in  STD_LOGIC;\n")
	f.write("\t\tstart : in STD_LOGIC;\n")
	f.write("\t\ts_out_r : out  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_out_i : out  STD_LOGIC_VECTOR (7 downto 0)\n")
	f.write("\t);\n")
	f.write("END component;\n\n")
		
	f.write("signal clk : std_logic := '0';\n")
	f.write("signal rst : std_logic := '0';\n")
	f.write("signal start : std_logic := '0';\n\n")

	f.write("signal s_out_r : std_logic_vector(7 downto 0) := X\"00\";\n")
	f.write("signal s_out_i : std_logic_vector(7 downto 0) := X\"00\";\n\n")
	   
	f.write(" constant clk_period : time := 10 ns;\n\n")
	 
	f.write("BEGIN\n\n")
	 
	f.write("uut: vec_mul PORT MAP (\n")
	f.write("\t\tclk => clk,\n")
	f.write("\t\trst => rst,\n")
	f.write("\t\tstart => start,\n")
	f.write("\t\ts_out_r => s_out_r,\n")
	f.write("\t\ts_out_i => s_out_i\n")
	f.write("\t);\n\n")

	f.write("clk_process :process\n")
	f.write("\tbegin\n")
	f.write("\t\tclk <= '0';\n")
	f.write("\t\twait for clk_period/2;\n")
	f.write("\t\tclk <= '1';\n")
	f.write("\t\twait for clk_period/2;\n")
	f.write("\tend process;\n\n")
	 

	f.write("stim_proc: process\n")
	f.write("\tbegin\n")		
	f.write("\t\twait for clk_period*10;\n")
	f.write("\t\twait for clk_period*3/10;\n")
	f.write("\t\trst <= '1';\n")
	f.write("\t\tstart <= '1';\n")
	f.write("\t\twait for clk_period;\n")
	f.write("\t\trst <='0';\n")
	f.write("\t\twait for clk_period*6;\n")
	f.write("\t\twait for clk_period*2*%d;\n"%l)
	f.write("\t\twait for clk_period*%d;\n"%(t-1))
	f.write("\t\tassert s_out_r = \"%s\"\n"%('{0:08b}'.format(rr)))
	f.write("\t\t\treport \"s_out_r error\" severity FAILURE;\n")
	f.write("\t\tassert s_out_i = \"%s\"\n"%('{0:08b}'.format(ri)))
	f.write("\t\t\treport \"s_out_i error\" severity FAILURE;\n")
	f.write("\t\twait;\n")
	f.write("\tend process;\n")

	f.write("END;\n")
	f.close()

def gen_tb_csa(n,a,r,d,result,l):
	rr = int(result.real)
	ri = int(result.imag)
	if (rr<0):
		rr = ((abs(rr) ^ 0b11111111) + 1) & 0b11111111
	if (ri<0):
		ri = ((abs(ri) ^ 0b11111111) + 1) & 0b11111111
	rr = rr & 0b11111111
	ri = ri & 0b11111111
	t = int(math.ceil(float(a)/float(n)))
	
	f = open("%s/tb_vec_mul.vhd"%d,'w')
	f.write("library IEEE;\n")
	f.write("use IEEE.STD_LOGIC_1164.ALL;\n\n")
	f.write("ENTITY tb_vec_mul IS\n")
	f.write("END tb_vec_mul;\n\n")
	 
	f.write("ARCHITECTURE behavior OF tb_vec_mul IS\n\n") 
	 
	f.write("COMPONENT vec_mul\n")
	f.write("\tPORT(\n")
	f.write("\t\tclk : in  STD_LOGIC;\n")
	f.write("\t\trst : in  STD_LOGIC;\n")
	f.write("\t\tstart : in STD_LOGIC;\n")
	f.write("\t\ts_out_r : out  STD_LOGIC_VECTOR (7 downto 0);\n")
	f.write("\t\ts_out_i : out  STD_LOGIC_VECTOR (7 downto 0)\n")
	f.write("\t);\n")
	f.write("END component;\n\n")
		
	f.write("signal clk : std_logic := '0';\n")
	f.write("signal rst : std_logic := '0';\n")
	f.write("signal start : std_logic := '0';\n\n")

	f.write("signal s_out_r : std_logic_vector(7 downto 0) := X\"00\";\n")
	f.write("signal s_out_i : std_logic_vector(7 downto 0) := X\"00\";\n\n")
	   
	f.write(" constant clk_period : time := 10 ns;\n\n")
	 
	f.write("BEGIN\n\n")
	 
	f.write("uut: vec_mul PORT MAP (\n")
	f.write("\t\tclk => clk,\n")
	f.write("\t\trst => rst,\n")
	f.write("\t\tstart => start,\n")
	f.write("\t\ts_out_r => s_out_r,\n")
	f.write("\t\ts_out_i => s_out_i\n")
	f.write("\t);\n\n")

	f.write("clk_process :process\n")
	f.write("\tbegin\n")
	f.write("\t\tclk <= '0';\n")
	f.write("\t\twait for clk_period/2;\n")
	f.write("\t\tclk <= '1';\n")
	f.write("\t\twait for clk_period/2;\n")
	f.write("\tend process;\n\n")
	 

	f.write("stim_proc: process\n")
	f.write("\tbegin\n")		
	f.write("\t\twait for clk_period*10;\n")
	f.write("\t\twait for clk_period*3/10;\n")
	f.write("\t\trst <= '1';\n")
	f.write("\t\tstart <= '1';\n")
	f.write("\t\twait for clk_period;\n")
	f.write("\t\trst <='0';\n")
	f.write("\t\twait for clk_period*6;\n")
	f.write("\t\twait for clk_period*%d;\n"%(l//r))
	f.write("\t\twait for clk_period*%d;\n"%(t-1))
	f.write("\t\tassert s_out_r = \"%s\"\n"%('{0:08b}'.format(rr)))
	f.write("\t\t\treport \"s_out_r error\" severity FAILURE;\n")
	f.write("\t\tassert s_out_i = \"%s\"\n"%('{0:08b}'.format(ri)))
	f.write("\t\t\treport \"s_out_i error\" severity FAILURE;\n")
	f.write("\t\twait;\n")
	f.write("\tend process;\n")

	f.write("END;\n")
	f.close()

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', type=int, required=True, help='number of entries processed in parallel')
	parser.add_argument('-a', type=int, required=True, help='total number of entries')
	parser.add_argument('-t', type=int, required=True, help='type of circuit 0=dsp, 1=csa')
	parser.add_argument('-r', type=int, help='register density, smaller r value results higher density')
	args = parser.parse_args()
	n = args.n
	a = args.a
	t = args.t
	wd = os.getcwd()
	if (t==0):
		d = wd+"\\"+`n`+"_"+`a`
	else:
		d = wd+"\\"+`n`+"_"+`a`+"csa"
		r = args.r
	if not os.path.exists(d):
		os.makedirs(d)
	m = n/4
	result = genData(a,m,d)
	genRAM(d)
	gen_accum(d)
	gen_counter(d)
	gen_mplx(d)
	gen_dsp_adder(d)
	gen_dsp_adder_5(d)
	if (t==0):
		l = gen_u_circuit_2(m,d)
		gen_circuit(d)
		gen_tb(n,a,d,result,l)
		gen_sim_script(n,a,d)
	else:
		gen_full_adder(d)
		gen_csa_2_3(d)
		gen_CLA(d)
		gen_CLA4(d)
		gen_reg_8(d)
		gen_circuit_csa(d)
		l = gen_u_circuit_csa(m, r, d)
		gen_tb_csa(n,a,r,d,result,l)
		gen_sim_script_csa(n,a,d)
	gen_top_modul_2(n,a,d)

main()