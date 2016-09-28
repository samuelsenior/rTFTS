# rTFTS
A python script that views the TalesFromTechSupport subreddit in Terminal. Display the top n number of posts, filter them by flair, sort them by hot, new, rising, etc and choose which one you want to read.

To choose the number of posts, flair, and sorting method call rTFTS in Terminal with the arguments -n [number], -f [flair], and -s [sort], where [number] is the number of posts to display (default is 10), [flair] is the flair (default is no flair filtering) and [sort] is the method of sorting (default is hot).

rTFTS can be set to loop around the main menu instead of closing after a post is displayed. To do this call rTFTS with ‘-p True’ from terminal (the default value is False). Inside this looping menu the number of posts, flair, and sorting method can all be set with the same commands as above, though only one can be set on each input.