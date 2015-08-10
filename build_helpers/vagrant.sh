[ -z $(vagrant box list | grep -o ubuntu-lts-icfpc) ] && vagrant box add ubuntu-lts-icfpc https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box
[ -f Vagrantfile ] || vagrant init ubuntu-lts-icfpc
vagrant up
