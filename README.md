# Novation nocturn Python library

Working version of a library to manage this great device
and use it in any midi or non midi project.

This library was developed for Linux.

This code is based on the sgreat work from Felicia (<https://github.com/Drachenkaetzchen/nocturn-game>)

It requires pyusb library that can be installed as follows:

pip3 install pyusb

It also required to add a rule for this vendor id
in the usb modem rules file at the following path:

/etc/udev/rules.d

Otherwise the python process must executed with SUDO.
