docker_installation_script 'default' do
    repo 'main'
    script_url 'https://my.computers.biz/dist/scripts/docker.sh'
    action :create
  end

docker_image 'nginx-alpine' do
    action :pull
  end