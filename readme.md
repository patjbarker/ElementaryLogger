# What's this?

This is my first Python-built malware, specifically a keylogger. It has very basic features, such as logging keys and
grabbing clipboard contents. Rather than using something like pyHook, I wanted to use a more non-traditional method of
using the Windows C libraries. This especially allowed for some good practice calling Windows functions.

# How to run?

Just run the main.py script and it'll execute the keylogging portion. To stop it, just kill the script in the processes.
