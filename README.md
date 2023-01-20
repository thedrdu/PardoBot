# PardoBot
### A fullstack Discord Bot for fun and utility!

Coded in python3.10.4 using the disnake library.

[pardobot.com](http://pardobot.com)

## Commands

```/latesttweet``` – Retrieves the latest official Honkai Impact 3rd tweet  
```/confignews``` – Configure which text channel to receive news posts in  
```/resetnews``` – Reset the text channel to receieve news posts in  
```/wikisearch``` – Search the official Honkai Impact 3rd Wiki  
```/configstats``` – Configure HoYoLAB tokens and settings to enable viewing of in-game stats(careful with this!)  
```/stats``` – View in-game stats(must be configured with ```/configstats``` first)  

Back-end: SQLite3, Nginx, uWSGI  
Bot: disnake + Python  
Front-end: Flask, Bootstrap  
