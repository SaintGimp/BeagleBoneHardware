echo gimp-uart1-00A0.dts -\> gimp-uart1-00A0.dtbo
dtc -O dtb -o gimp-uart1-00A0.dtbo -b 0 -@ -I dts gimp-uart1-00A0.dts

echo gimp-uart2-00A0.dts -\> gimp-uart2-00A0.dtbo
dtc -O dtb -o gimp-uart2-00A0.dtbo -b 0 -@ -I dts gimp-uart2-00A0.dts

echo gimp-uart4-00A0.dts -\> gimp-uart4-00A0.dtbo
dtc -O dtb -o gimp-uart4-00A0.dtbo -b 0 -@ -I dts gimp-uart4-00A0.dts

echo gimp-uart5-00A0.dts -\> gimp-uart5-00A0.dtbo
dtc -O dtb -o gimp-uart5-00A0.dtbo -b 0 -@ -I dts gimp-uart5-00A0.dts
