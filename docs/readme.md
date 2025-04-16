# Assembly of the Raspberry Pi 5 with Screen for the FaceAuth Project

This tutorial explains, in a very simple way, how to assemble the facial recognition system (**FaceAuth**) using the **Raspberry Pi 5** and a **touchscreen display**.

This guide is designed for people who have never assembled hardware before.

**Prefer a video?** You can follow this tutorial for part 6 (Mounting the Raspberry Pi to the screen):  
[YouTube Tutorial](https://www.youtube.com/watch?v=QhdRg2x6vxo)

---

## 1. Materials Needed for the Project

- Raspberry Pi 5  
- Camera  
- Touchscreen Display  
- Power Supply  
- Case with Active Heatsink (cooler)  
- MicroSD Card  
- CSI Cable for Camera

---

## 2. Models of Materials Used

- **Raspberry Pi 5** Model B (8GB RAM)  
- **Camera**: Raspberry Pi Camera Module V2 (8MP) – Official  
- **Display**: LUCKFOX 7" HDMI Touchscreen (1024x600)  
- **Power Supply**: Miuzei 5.1V 5A USB-C (27W)  
- **Cooling**: Miuzei Heatsink with Fan  
- **Storage**: SanDisk Ultra 64GB MicroSDHC Class 10  
- **Cable**: Waveshare CSI FPC Flexible Cable (22-pin to 15-pin)

---

## 3. Preparation

Before starting, make sure you have:

- All the materials.
- Simple tools (or those included with the cooler).
- A clean and safe workspace.

---

## 4. Install Raspberry Pi OS on the MicroSD Card

1. Insert the MicroSD card into your computer using a card reader.  
2. Download and install the **Raspberry Pi Imager** from the official website.  
3. Open the application and select:
   - **Device**: Raspberry Pi 5
   - **OS**: Raspberry Pi OS  
4. Click **"Write"** and wait for the process to complete.  
5. Safely eject the MicroSD card and insert it into the **Raspberry Pi’s card slot** (back side).

---

## 5. Mount the Heatsink and Fan (Cooler) on the Raspberry Pi

1. Stick the **thermal pads** on the main components as shown in the heatsink box.  
2. Remove the film from the top of the pads.  
3. Align and screw the **metal heatsink** on top of the Raspberry Pi.  
4. Connect the **fan cable**:
   - Plug into the fan header near the USB ports.
   - **Red wire** faces **inward**, **yellow wire** outward.
   - Be careful removing the plastic protector before connecting.

---

## 6. Mount the Raspberry Pi to the Screen

### Connect the FPC Image Cable

1. Locate the small connector on the back of the screen near HDMI port.  
2. Open the latch gently.  
3. Insert the **FPC cable**:
   - **Metal connectors facing up**
   - **Black side of the cable facing down**  
4. Close the latch carefully.
5. then the other end of this cable will connect to the connector that has a minidisplay port and when we look at it  from behind where we open the connector we connect the cable with the black part facing the back and the connectors facing the front.

### Attach the Raspberry to the Screen

1. Remove the adhesive films on the mounting area.  
2. Align the Raspberry Pi with the power button facing the gray HDMI port.
3. Gently place the Raspberry Pi and secure it with **4 screws**.  
4. Ensure the **FPC cable is not stressed or bent**.

### Connect the Remaining Cables

- **HDMI Cable**: Connect Raspberry’s HDMI to the screen’s HDMI.  
- **USB Cable**:  
  - Plug into the **"Touch"** port on the screen.  
  - Connect to a USB port on the Raspberry Pi.
- **Power Cable (3 wires)**:  
  - Plug into the **"Power"** port on the screen.  
  - Connect to the GPIO pins on the Raspberry, matching wire order (black to the edge).

---

## 7. Test the Screen

- Plug the Raspberry Pi into power.  
- The screen should turn on.  
- The touchscreen may take a few seconds to be recognized.

---

## 8. Connect the Camera

1. **Turn off** the Raspberry Pi.  
2. Use the **new flexible cable** (not the short one that came with the camera).  

### On the Camera:

- Open the connector and insert the cable:  
  - **Metal connectors facing the lens**.

### On the Raspberry Pi:

- The camera connector is behind the Ethernet port.  
- Open the latch, insert the cable:  
  - **Metal connectors facing the Ethernet port**.  
- Close the latch securely.

---

## Done!

The **Raspberry Pi**, **screen**, and **camera** are now fully assembled and ready to run **FaceAuth**!
