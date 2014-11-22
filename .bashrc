case "$TERM" in
  xterm*)
    source ~/.bash.d/bashrc-xterm
    ;;
  rxvt*)
    source ~/.bash.d/bashrc-rxvt-unicode
    ;;
  *)
    ;;
esac
