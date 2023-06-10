# stop_and_wait
A stop and wait reliable transmission protocol written in Python which uses a retransmission timer inspired by TCP's retransmission timer. This was designed and developed as a learning excercise to learn more about how reliable transmission protocols work. The current sender implementation takes a filepath as a command line argument and sends the file to the receiver defined in the config file.

# Instructions
No third party dependencies are required to run the program. First, you must modify the config file to match the IP/Port you wish to use for the sender and receiver hosts.

After modifying the config file, you can run the receiver:

```
python3 receiver.py
```

Then, run the sender:

```
python3 sender.py <filepath>
```
