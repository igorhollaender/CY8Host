#*******************************************************************************
#
#	C Y 8 H o s t . p y 
#
#
#	Last revision: 171024 IH
#
#*******************************************************************************
# 	Adapted from Python_Ex.py included in Cypress distribution 
#	- adapted to python 3  (print xxx --> print(xxx) , raw_input --> input
#
# 	Other adaptations 
#	- changed ord(x) to x at several places 
#
#*******************************************************************************

#*******************************************************************************
#	Notes:
#	
#	To install win32com.client, do
# 		python -m pip install pypiwin32'   
#	(see https://stackoverflow.com/questions/23864234/importerror-no-module-named-win32com-client )
#
#*******************************************************************************



#*******************************************************************************
#  Original Cypress Disclaimer:
#
#*******************************************************************************
#* © 2011-2017, Cypress Semiconductor Corporation
#* or a subsidiary of Cypress Semiconductor Corporation. All rights
#* reserved.
#* 
#* This software, including source code, documentation and related
#* materials (“Software”), is owned by Cypress Semiconductor
#* Corporation or one of its subsidiaries (“Cypress”) and is protected by
#* and subject to worldwide patent protection (United States and foreign),
#* United States copyright laws and international treaty provisions.
#* Therefore, you may use this Software only as provided in the license
#* agreement accompanying the software package from which you
#* obtained this Software (“EULA”).
#* 
#* If no EULA applies, Cypress hereby grants you a personal, non-
#* exclusive, non-transferable license to copy, modify, and compile the
#* Software source code solely for use in connection with Cypress’s
#* integrated circuit products. Any reproduction, modification, translation,
#* compilation, or representation of this Software except as specified
#* above is prohibited without the express written permission of Cypress.
#* 
#* Disclaimer: THIS SOFTWARE IS PROVIDED AS-IS, WITH NO
#* WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING,
#* BUT NOT LIMITED TO, NONINFRINGEMENT, IMPLIED
#* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#* PARTICULAR PURPOSE. Cypress reserves the right to make
#* changes to the Software without notice. Cypress does not assume any
#* liability arising out of the application or use of the Software or any
#* product or circuit described in the Software. Cypress does not
#* authorize its products for use in any products where a malfunction or
#* failure of the Cypress product may reasonably be expected to result in
#* significant property damage, injury or death (“High Risk Product”). By
#* including Cypress’s product in a High Risk Product, the manufacturer
#* of such system or application assumes all risk of such use and in doing
#* so agrees to indemnify Cypress against all liability.
#********************************************************************************

import win32com.client
import array

import PPCOM
from PPCOM import enumInterfaces
from PPCOM import enumFrequencies
from PPCOM import enumSonosArrays

import tkinter as tk
import tkinter.scrolledtext as tkst


#********************************************************************************
class MyGUI(tk.Frame):

#  tutorial:  http://zetcode.com/gui/tkinter/menustoolbars/

    def __init__(self,programmer):
        super().__init__()
        self.programmer = programmer
        self.initUI()
        
    def initUI(self):
        self.master.geometry("750x450")
        self.master.title("Liquid Level Gauge Demonstrator")
		
        # frame layout
        topFrame = tk.Frame(
            master = self.master
            )
        bottomFrame = tk.Frame(
            master = self.master
            )        
        bottomFrame.pack(
            fill        =   'both',
            side        =   'bottom'
            )
        topFrame.pack(
            fill        =   'both'
            )        
            
        # console output	
        self.consoleOutput = tkst.ScrolledText(
             master     = bottomFrame,
			 wrap       = 'word',
             height     = 10
			 )
        self.consoleOutput.pack(
            fill        ='x',
            expand      =   True
            )
            
		# top menu		
        menuBar = tk.Menu(
            master      =   self.master
            )            
        self.master.config(menu=menuBar)
        
        fileMenu = tk.Menu(menuBar)
        fileMenu.add_command(
            label       =   "Exit", 
            command     =   self.onExit
            )
        menuBar.add_cascade(
            label       =   "File", 
            menu        =   fileMenu
            )
            
        programmerMenu = tk.Menu(menuBar)        
        menuBar.add_cascade(
            label       =   "Programmer", 
            menu        =   programmerMenu
            )        
                    
        programmerMenu.add_command(
            label       =   "Execute", 
            command     =   self.Programmer_Execute
            )        
                                            
        # canvas    
        self.canvas = tk.Canvas(
            )
        self.canvas.pack(
            fill        ='both',
            expand      =   True
            )            
            
        #IH171024 for debugging only  
        self.canvas.create_rectangle(30, 10, 120, 80, 
            outline="#fb0", fill="#fb0")
            
		            
    # callbacks     	
    def onExit(self):	
        self.quit()
        
    # miscellaneous
    def PrintToConsole(self,text):
        self.consoleOutput.insert(tk.END,text+'\n')
        self.consoleOutput.update_idletasks()
        
    def Programmer_Execute(self):
        self.PrintToConsole("Working ...")                    
        hr = self.programmer.Execute()
        if (self.programmer.SUCCEEDED(hr)):
            str = "Succeeded!"
        else:
            str = "Failed! " + self.programmer.m_sLastError
        self.PrintToConsole(str)                    
	
#********************************************************************************

#********************************************************************************
class CypressProgrammer:

    #Define global variables
    m_sLastError = ""

    #Error constants
    S_OK        = 0
    E_FAIL      = -1

    #Chip Level Protection constants
    CHIP_PROT_VIRGIN        = 0x00
    CHIP_PROT_OPEN          = 0x01
    CHIP_PROT_PROTECTED     = 0x02
    CHIP_PROT_KILL          = 0x04
    CHIP_PROT_MASK          = 0x0F
   

    def __init__(self,hexFileToProgram):        
        self.hexFileToProgram = hexFileToProgram        
        self.pp = win32com.client.Dispatch("PSoCProgrammerCOM.PSoCProgrammerCOM_Object")
           
    def SUCCEEDED(self,hr):
        return hr >= 0

    def OpenPort(self):        
        # Open Port - get last (connected) port in the ports list
        hResult = self.pp.GetPorts()
        hr = hResult[0]
        portArray = hResult[1]
        self.m_sLastError = hResult[2]    
        if (not self.SUCCEEDED(hr)): return hr
        if (len(portArray) <= 0):
            self.m_sLastError = "Connect any Programmer to PC"
            return -1
        bFound = 0
        for i in range(0, len(portArray)):
            if (portArray[i].startswith("MiniProg3") or portArray[i].startswith("TrueTouchBridge") or portArray[i].startswith("KitProg")):
                portName = portArray[i]            
                bFound = 1
                break
        if(bFound == 0):
            self.m_sLastError = "Connect any MiniProg3/TrueTouchBridge/KitProg device to the PC"
            return -1

        #Port should be opened just once to connect Programmer device (MiniProg1/3,etc).
        #After that you can use Chip-/Programmer- specific APIs as long as you need.
        #No need to repoen port when you need to acquire chip 2nd time, just call Acquire() again.
        #This is true for all other APIs which get available once port is opened.
        #You have to call OpenPort() again if port was closed by ClosePort() method, or
        #when there is a need to connect to other programmer, or
        #if programmer was physically reconnected to USB-port.
                
        hr = self.pp.OpenPort(portName)
        self.m_sLastError = hr[1]
        return hr[0]

    def ClosePort(self):    
        hResult = self.pp.ClosePort()
        hr = hResult[0]
        strError = hResult[1]
        return hr

    def InitializePort(self):
        #Setup Power On
        self.pp.SetPowerVoltage("3.3")
        hResult = self.pp.PowerOn()
        hr = hResult[0]
        self.m_sLastError = hResult[1]
        if (not self.SUCCEEDED(hr)): return hr

        #Set protocol, connector and frequency
        hResult = self.pp.SetProtocol(enumInterfaces.SWD)
        hr = hResult[0]
        self.m_sLastError = hResult[1]
        if (not self.SUCCEEDED(hr)): return hr

        self.pp.SetProtocolConnector(0) #5-pin connector
        self.pp.SetProtocolClock(enumFrequencies.FREQ_03_0) #3.0 MHz clock on SWD bus
        
        return hr

    def CheckHexAndDeviceCompatibility(self):        
        listResult = []
        result = 0
        hResult = self.pp.PSoC4_GetSiliconID()
        hr = hResult[0]
        chipJtagID = hResult[1]
        self.m_sLastError = hResult[2]
        if (not self.SUCCEEDED(hr)):
            listResult.append(hr)
            listResult.append(result)
            return listResult
        hResult = self.pp.HEX_ReadJtagID()
        hr = hResult[0]
        hexJtagID = hResult[1]
        self.m_sLastError = hResult[2]
        if (not self.SUCCEEDED(hr)):
            listResult.append(hr)
            listResult.append(result)
            return listResult
        result = 1
        for i in range(0, 4):
            if (i == 2): continue #ignore revision, 11(AA),12(AB),13(AC), etc
            #IH171023 changed    ord(hexJtagID[0])   to    hexJtagID[0]
            #IH171023 changed    ord(chipJtagID[0])   to   chipJtagID[0]
            if(hexJtagID[i] != chipJtagID[i]):
                result = 0
                break
        listResult.append(0)
        listResult.append(result)
        return listResult

    def PSoC4_IsChipNotProtected(self):
        #Chip Level Protection reliably can be read by below API (available in VIRGIN, OPEN, PROTECTED modes)
        #This API uses SROM call - to read current status of CPUSS_PROTECTION register (privileged)
        #This register contains current protection mode loaded from SFLASH during boot-up.
        
        hResult = self.pp.PSoC4_ReadProtection()
        hr = hResult[0]
        flashProt = hResult[1]
        chipProt = hResult[2]
        self.m_sLastError = hResult[3]
        if (not self.SUCCEEDED(hr)): return self.E_FAIL #consider chip as protected if any communication failure
        
        #IH171023 changed    ord(chipProt[0])   to    chipProt[0]
        if ((chipProt[0] & self.CHIP_PROT_PROTECTED) == self.CHIP_PROT_PROTECTED):
            self.m_sLastError = "Chip is in PROTECTED mode. Any access to Flash is suppressed."        
            return self.E_FAIL

        return self.S_OK
        
    def PSoC4_EraseAll(self):        
        #Check chip level protection here. If PROTECTED then move to OPEN by PSoC4_WriteProtection() API.
        #Otherwise use PSoC4_EraseAll() - in OPEN/VIRGIN modes.

        hr = self.PSoC4_IsChipNotProtected()    
        if (self.SUCCEEDED(hr)): #OPEN mode
            #Erase All - Flash and Protection bits. Still be in OPEN mode.
            hResult = self.pp.PSoC4_EraseAll()
            hr = hResult[0]
            self.m_sLastError = hResult[1]        
        else:
            #Move to OPEN from PROTECTED. It automatically erases Flash and its Protection bits.
            flashProt = [] #do not care in PROTECTED mode
            chipProt = []
            for i in range(0, 1):
                chipProt.append(self.CHIP_PROT_OPEN)
            data1 = array.array('B',flashProt) #do not care in PROTECTED mode
            data2 = array.array('B',chipProt)  #move to OPEN

            hResult = self.pp.PSoC4_WriteProtection(buffer(data1), buffer(data2))
            hr = hResult[0]
            self.m_sLastError  = hResult[1]        
            if (not self.SUCCEEDED(hr)): return hr

            #Need to reacquire chip here to boot in OPEN mode.
            #ChipLevelProtection is applied only after Reset.
            hResult = self.pp.DAP_Acquire()
            hr = hResult[0]
            self.m_sLastError  = hResult[1]
        return hr

    def PSoC4_GetTotalFlashRowsCount(self,flashSize):        
        hResult = self.pp.PSoC4_GetFlashInfo()
        hr = hResult[0]
        rowsPerArray = hResult[1]
        rowSize = hResult[2]
        self.m_sLastError = hResult[3]
        if (not self.SUCCEEDED(hr)): return hr

        totalRows = flashSize / rowSize

        return (hr,totalRows,rowSize)

    def ProgramFlash(self,flashSize):        
        hResult = self.PSoC4_GetTotalFlashRowsCount(flashSize)
        hr = hResult[0]
        totalRows = int(hResult[1])  #IH171023 changed    hResult[1]   to    int(hResult[1])	
        rowSize = int(hResult[2])  #IH171023 changed    hResult[2]   to    int(hResult[2])
        
        if (not self.SUCCEEDED(hr)): return hr    
        #Program Flash array
        for i in range(0, totalRows):
            hResult = self.pp.PSoC4_ProgramRowFromHex(i)
            hr = hResult[0]
            self.m_sLastError = hResult[1]
            if (not self.SUCCEEDED(hr)): return hr
        return hr    

    def PSoC4_VerifyFlash(self,flashSize):        
        hResult = self.PSoC4_GetTotalFlashRowsCount(flashSize)
        hr = hResult[0]
        totalRows = int(hResult[1])    #IH171023 changed    hResult[1]   to    int(hResult[1])	
        rowSize = int(hResult[2])      #IH171023 changed    hResult[2]   to    int(hResult[2])	
        if (not self.SUCCEEDED(hr)): return hr    
        #Verify Flash array
        for i in range(0, totalRows):        
            hResult = self.pp.PSoC4_VerifyRowFromHex(i)
            hr = hResult[0]
            verResult = int(hResult[1])  #IH171023 changed    hResult[1]   to    int(hResult[1])	
            self.m_sLastError = hResult[2]  
            if (not self.SUCCEEDED(hr)): return hr
            if (verResult == 0):
                self.m_sLastError = "Verification failed on %d row." % (i)
                return self.E_FAIL
        return hr

    def ProgramAll(self):        
        # Open Port - get last (connected) port in the ports list
        hr = self.InitializePort()
        if (not self.SUCCEEDED(hr)): return hr
        
        # Set Hex File
        hResult = self.pp.HEX_ReadFile(self.hexFileToProgram) #IH171023 for some reason this must reside in root
        hr = hResult[0]    
        hexImageSize = int(hResult[1])
        self.m_sLastError = hResult[2]
        if (not self.SUCCEEDED(hr)): return hr
        
        #Read chip level protection from hex and check Chip Level Protection mode
        #If it is VIRGIN then don't allow Programming, since it can destroy chip
        hResult = self.pp.HEX_ReadChipProtection()
        hr = hResult[0]
        hex_chipProt = hResult[1]
        self.m_sLastError = hResult[2]
            
        if (not self.SUCCEEDED(hr)): return hr
        #IH171023 changed    ord(hex_chipProt[0])   to    hex_chipProt[0]
        if (hex_chipProt[0] == self.CHIP_PROT_VIRGIN):
            self.m_sLastError = "Transition to VIRGIN is not allowed. It will destroy the chip. Please contact Cypress if you need this specifically."
            return self.E_FAIL

        # Set Acquire Mode
        self.pp.SetAcquireMode("Reset")

        #Acquire Device
        hResult = self.pp.DAP_Acquire()
        hr = hResult[0]
        self.m_sLastError = hResult[1]
        if (not self.SUCCEEDED(hr)): return hr
        
        #Check Hex File and Device compatibility
        fCompatibility = 0
        hResult = self.CheckHexAndDeviceCompatibility()
        hr = hResult[0]
        fCompatibility = hResult[1]    
        if (not self.SUCCEEDED(hr)): return hr
        if (fCompatibility == 0):
            self.m_sLastError = "The Hex file does not match the acquired device, please connect the appropriate device"
            return self.E_FAIL
        
        #Erase All
        hr = self.PSoC4_EraseAll()
        if (not self.SUCCEEDED(hr)): return hr

        #Find checksum of Privileged Flash. Will be used in calculation of User CheckSum later    
        hResult = self.pp.PSoC4_CheckSum(0x8000) #CheckSum All Flash ("Privileged + User" Rows)
        hr = hResult[0]
        checkSum_Privileged = hResult[1]
        self.m_sLastError = hResult[2]
        if (not self.SUCCEEDED(hr)): return hr

        #Program Flash
        hr = self.ProgramFlash(hexImageSize)
        if (not self.SUCCEEDED(hr)): return hr

        #Verify Rows
        hr = self.PSoC4_VerifyFlash(hexImageSize)
        if (not self.SUCCEEDED(hr)): return hr
        
        #Protect All arrays
        hResult = self.pp.PSoC4_ProtectAll()
        hr = hResult[0]
        self.m_sLastError = hResult[0]
        if (not self.SUCCEEDED(hr)): return hr
        
        #Verify protection ChipLevelProtection and Protection data
        hResult = self.pp.PSoC4_VerifyProtect()
        hr = hResult[0]
        self.m_sLastError = hResult[0]
        if (not self.SUCCEEDED(hr)): return hr
        
        #CheckSum verification
        hResult = self.pp.PSoC4_CheckSum(0x8000) #CheckSum All Flash (Privileged + User)
        hr = hResult[0]
        checkSum_UserPrivileged = hResult[1]
        self.m_sLastError = hResult[2]
        if (not self.SUCCEEDED(hr)): return hr
        checkSum_User = checkSum_UserPrivileged - checkSum_Privileged #find checksum of User Flash rows
        
        hResult = self.pp.HEX_ReadChecksum()
        hr = hResult[0]
        hexChecksum = hResult[1]
        self.m_sLastError = hResult[2]
        if (not self.SUCCEEDED(hr)): return hr
        checkSum_User = checkSum_User & 0xFFFF
        hexChecksum = hexChecksum & 0xFFFF
        
        if (checkSum_User != hexChecksum):
            myPrint ("Mismatch of Checksum: Expected 0x%x, Got 0x%x" %(checkSum_User, hexChecksum))        
            return self.E_FAIL
        else:
            myPrint ("Checksum 0x%x" %(checkSum_User))    
            pass

        #Release PSoC3 device
        hResult = self.pp.DAP_ReleaseChip()
        hr = hResult[0]
        self.m_sLastError = hResult[1]
        
        return hr

    def UpgradeBlock(self):
        # Open Port - get last (connected) port in the ports list
        hr = self.InitializePort()
        if (not self.SUCCEEDED(hr)): return hr

        # Set Acquire Mode
        self.pp.SetAcquireMode("Reset")

        #Acquire Device
        hResult = self.pp.DAP_Acquire()
        hr = hResult[0]
        self.m_sLastError = hResult[1]
        if (not self.SUCCEEDED(hr)): return hr

        #Write Block, use PSoC4_WriteRow() instead PSoC3_ProgramRow()
        hResult = self.pp.PSoC4_GetFlashInfo()
        hr = hResult[0]
        rowsPerArray = hResult[1]
        rowSize = hResult[2]
        self.m_sLastError = hResult[3]
        if (not self.SUCCEEDED(hr)): return hr

        writeData = [] #User and Config area of the Row (256+32)    
        for i in range(0, rowSize):
            writeData.append(i & 0xFF)
        data = array.array('B',writeData)
        rowID = rowSize - 1
        hResult = self.pp.PSoC4_WriteRow(rowID, buffer(data))
        hr = hResult[0]
        self.m_sLastError = hResult[1]
        if (not self.SUCCEEDED(hr)): return hr

        #Verify Row - only user area (without Config one)
        hResult = self.pp.PSoC4_ReadRow(rowID)
        hr = hResult[0]
        readData = hResult[1]
        self.m_sLastError = hResult[2]
        if (not self.SUCCEEDED(hr)): return hr
        
        for i in range(0, len(readData)):  #check 128 bytes        
            if (ord(readData[i]) != writeData[i]):
                hr = self.E_FAIL
                break
            
        if (not self.SUCCEEDED(hr)):
            self.m_sLastError = "Verification of User area failed!"
            return hr

        #Release PSoC4 chip
        hResult = self.pp.DAP_ReleaseChip()
        hr = hResult[0]
        self.m_sLastError = hResult[1]
        
        return hr

    def Execute(self):    
        hr = self.OpenPort()
        if (not self.SUCCEEDED(hr)): return hr
        hr = self.ProgramAll()
        # hr = self.UpgradeBlock()
        self.ClosePort()
        return hr

      
#********************************************************************************

def myPrint(text):
   global myGUI
   myGUI.PrintToConsole(text) 
      
#********************************************************************************

version = "171014a"

cypressProgrammer = CypressProgrammer(hexFileToProgram="C:\\IH_CapGauge02.hex") 
#IH171023 for some reason this must reside in root

root = tk.Tk()
myGUI = MyGUI(programmer=cypressProgrammer)
myPrint("Liquid Level Gauge Demonstrator, Version %s"%version)

root.mainloop()
