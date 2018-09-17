# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.hostname = "matchingbox"
  config.vm.define "matchingbox"
  config.vm.network "forwarded_port", guest: 5432, host: 5432

  config.vm.provision :shell,
    path: "scripts/vagrant/provision.sh",
    privileged: false
  config.vm.provision :shell,
    path: "scripts/vagrant/up.sh",
    privileged: false,
    run: "always"
end
