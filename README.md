# stop_and_wait
A stop and wait reliable transmission protocol written in Python which uses a retransmission timer inspired by TCP's retransmission timer. 
This was designed and developed as a learning excercise to learn more about how reliable transmission protocols work.

Run the server:
```console
python3 server.py ip port
```

Then, run the client:

```console
python3 client.py server_ip server_port filepath
```
