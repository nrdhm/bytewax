mkfifo other_fifo
mkfifo some_fifo

function gen_big_str {
        echo $(cat /dev/urandom| head -c $(( 90 * 1024  )) | base64 -w 0)
}


i=0; while true; do echo $i;
        gen_big_str >> some_fifo; echo '' >> some_fifo;
i=$(($i +1)); done


i=0; while true; do echo $i;
        gen_big_str >> other_fifo; echo '' >> other_fifo;
i=$(($i +1)); done
