FROM tutum/buildstep
EXPOSE 5000

CMD ["/bin/bash", "/app/contrib/docker/initapp.sh"]
