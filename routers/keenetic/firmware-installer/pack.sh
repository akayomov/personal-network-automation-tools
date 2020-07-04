FIRMWARE_NAME="core.firmware.tar.gz"

echo "Cleanup existing package"
if [ -f "./$FIRMWARE_NAME" ]; then rm ./$FIRMWARE_NAME; fi
echo "Packing script file into package"
tar czf ./$FIRMWARE_NAME bin etc lib sbin
echo "Done"
