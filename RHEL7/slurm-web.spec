# Turn off the Fascist build policy (ignore unused files)
%define _unpackaged_files_terminate_build 0 

Name:           Slurm-web
Version:        1.1.3
Release:        1%{?dist}
Summary:        Slurm-web is web application that serves as web frontend to Slurm workload manager.

License:        GPLv2+
URL:            http://edf-hpc.github.io/slurm-web/
Source0:        https://github.com/edf-hpc/slurm-web

BuildArch:      noarch
Requires:       slurm-web-dashboard
Requires:       slurm-web-restapi

%description
Slurm-web is web application that serves as web frontend to Slurm workload manager.

%package -n slurm-web-dashboard
Summary:    Slurm-web interface
BuildArch:  noarch
Requires:   libjs-bootstrap
Requires:   js-jquery
Requires:   libjs-jquery-flot
Requires:   httpd
Requires:   httpd-devel

%description -n slurm-web-dashboard
The role of the dashboard is to show to users, administrators and decidors all supercomputer runtime data in a graphical and attractive way. It is a web GUI that aims to be user-friendly, beautiful and clean. The dashboard is developed in HTML and Javascript. It is designed to be used with any modern web browser with fairly decent support of HTML5, Javascript and CSS.

%package -n slurm-web-restapi
Summary:    Slurm-web backend api
BuildArch:  noarch
Requires:   python
Requires:   clustershell
#Requires:   python-clustershell
Requires:   python-flask
Requires:   python-pyslurm

%description -n slurm-web-restapi
The role of the API is to serve raw runtime data about a system (typically a supercomputer) running Slurm. All data are delivered in common and standard JSON format. This backend API is developed in Python programming language.

%prep

%build

%install

# Install apache conf files
mkdir -p $RPM_BUILD_ROOT/etc/httpd/conf.d
install -m 644 slurm-web/conf/slurm-web-dashboard.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/slurm-web-dashboard.conf
install -m 644 slurm-web/conf/slurm-web-restapi.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/slurm-web-restapi.conf 

# Install racks configuration file
mkdir -p $RPM_BUILD_ROOT/etc/slurm-web
install -m 644 slurm-web/conf/racks.xml $RPM_BUILD_ROOT/etc/slurm-web/racks.xml

# Install remaining dashboard files
mkdir -p $RPM_BUILD_ROOT/usr/share/slurm-web
mkdir -p $RPM_BUILD_ROOT/usr/share/slurm-web/dashboard
mkdir -p $RPM_BUILD_ROOT/usr/share/slurm-web/dashboard/css
mkdir -p $RPM_BUILD_ROOT/usr/share/slurm-web/dashboard/static
mkdir -p $RPM_BUILD_ROOT/usr/share/slurm-web/dashboard/js
install -m 644 slurm-web/html/index.html $RPM_BUILD_ROOT/usr/share/slurm-web/dashboard/index.html
install -m 644 slurm-web/css/dashboard.css $RPM_BUILD_ROOT/usr/share/slurm-web/dashboard/css/dashboard.css
install -m 644 slurm-web/static/logo.png $RPM_BUILD_ROOT/usr/share/slurm-web/dashboard/static/logo.png
install -m 644 slurm-web/js/slurm-dashboard.js $RPM_BUILD_ROOT/usr/share/slurm-web/dashboard/js/slurm-dashboard.js

# Install remaining restapi files 
mkdir -p $RPM_BUILD_ROOT/usr/share/slurm-web
mkdir -p $RPM_BUILD_ROOT/usr/share/slurm-web/restapi
mkdir -p $RPM_BUILD_ROOT/usr/share/slurm-web/restapi/schema
mkdir -p $RPM_BUILD_ROOT/usr/share/slurm-web/restapi/schema/dtd
install -m 644 slurm-web/rest/slurmrestapi.py $RPM_BUILD_ROOT/usr/share/slurm-web/restapi/slurm-web-restapi.wsgi
install -m 644 slurm-web/rest/slurmrestapi.py $RPM_BUILD_ROOT/usr/share/slurm-web/restapi/slurmrestapi.py
install -m 644 slurm-web/schema/racks.dtd $RPM_BUILD_ROOT/usr/share/slurm-web/restapi/schema/dtd/racks.dtd

# Install doc files
install -m 644 slurm-web/README.md $RPM_BUILD_ROOT/usr/share/slurm-web/README.md
install -m 644 slurm-web/COPYING $RPM_BUILD_ROOT/usr/share/slurm-web/COPYING

# start apache server if not already started, otherwise restart
systemctl restart httpd

#start flask app
#python $RPM_BUILD_ROOT/usr/share/slurm-web/restapi/slurmrestapi.py

%files
%doc /usr/share/slurm-web/README.md
%doc /usr/share/slurm-web/COPYING

%files -n slurm-web-dashboard
/etc/httpd/conf.d/slurm-web-dashboard.conf 
/usr/share/slurm-web/dashboard/css/dashboard.css 
/usr/share/slurm-web/dashboard/static/logo.png 
/usr/share/slurm-web/dashboard/js/slurm-dashboard.js 
/usr/share/slurm-web/dashboard/index.html

%files -n slurm-web-restapi
/etc/slurm-web/racks.xml 
/etc/httpd/conf.d/slurm-web-restapi.conf 
/usr/share/slurm-web/restapi/slurm-web-restapi.wsgi 
/usr/share/slurm-web/restapi/slurmrestapi.py 
/usr/share/slurm-web/restapi/schema/dtd/racks.dtd

%changelog