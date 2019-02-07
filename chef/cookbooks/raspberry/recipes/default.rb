docker_installation_script 'default' do
    repo 'main'
    script_url 'https://gist.githubusercontent.com/pawelros/2ec289da8783ecb82e1fe951104dc3c3/raw/e76efc9e8dbde69bb802f0e8bcd85a8bdf0b9946/get-docker.sh'
    action :create
  end

  execute 'add rosiu to docker group' do
    command 'sudo gpasswd -a rosiu docker && newgrp docker'
  end

docker_image 'nginx' do
    tag '1.14.1-alpine'
    action :pull
  end