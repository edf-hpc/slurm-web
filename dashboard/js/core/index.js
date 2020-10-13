/*
 * Copyright (C) 2015 EDF SA
 *
 * This file is part of slurm-web.
 *
 * slurm-web is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * slurm-web is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with slurm-web.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

var isIE = Boolean(document.documentMode);

require.config({
  paths: {
    text: '/javascript/requirejs/text.min',
    jquery: '/javascript/jquery/jquery.min',
    'jquery-tablesorter': '/javascript/jquery-tablesorter/jquery.tablesorter.min',
    'jquery-flot': '/javascript/jquery-flot/jquery.flot.min',
    'jquery-flot-pie': '/javascript/jquery-flot/jquery.flot.pie.min',
    xdomain: '../../js/libraries/xdomain.min',
    async: '/javascript/async/async.min',
    handlebars: '/javascript/handlebars/handlebars',
    bootstrap: '/javascript/bootstrap/js/bootstrap',
    'bootstrap-typeahead': '/javascript/bootstrap/js/typeahead.jquery',
    'bootstrap-tagsinput': '/javascript/bootstrap/js/bootstrap-tagsinput.min',
    d3: '/javascript/d3/d3.min',
    'token-utils': '../../js/utils/token',
    'user-utils': '../../js/utils/user',
    'date-utils': '../../js/utils/date',
    'tablesorter-utils': '../../js/utils/tablesorter',
    'jobs-utils': '../../js/utils/jobs',
    'page-utils': '../../js/utils/page',
    'ajax-utils': '../../js/utils/ajax',
    'error-utils': '../../js/utils/error',
    'flot-utils': '../../js/utils/flot',
    'tagsinput-utils': '../../js/utils/tagsinput',
    'string-helpers': '../../js/helpers/string',
    'jobs-helpers': '../../js/helpers/jobs',
    'number-helpers': '../../js/helpers/number',
    'boolean-helpers': '../../js/helpers/boolean',
    'date-helpers': '../../js/helpers/date',
    'different-helpers': '../../js/helpers/different',
    'keycode-helpers': '../../js/helpers/keycode',
    'view-helpers': '../../js/helpers/view',
    '2d-draw': '../../js/draw/2d-draw',
    'colors-draw': '../../js/draw/colors',
    '2d-intersections-draw': '../../js/draw/2d-intersections',
    '2d-legend-draw': '../../js/draw/2d-legend',
    'factor-draw': '../../js/draw/factor',
    login: '../../js/core/login/login',
    navbar: '../../js/core/navbar/navbar',
    clusters: '../../js/core/clusters/clusters',
    jobs: '../../js/modules/jobs/jobs',
    racks: '../../js/modules/racks/racks',
    'jobs-map': '../../js/modules/jobs-map/jobs-map',
    partitions: '../../js/modules/partitions/partitions',
    reservations: '../../js/modules/reservations/reservations',
    qos: '../../js/modules/qos/qos',
    '3d-view': '../../js/modules/3d-view/3d-view',
    gantt: '../../js/modules/gantt/gantt',
    topology: '../../js/modules/topology/topology',
    'topology-utils': '../../js/utils/topology',
    'fake-placeholder': '../../js/utils/fakePlaceholder',
    sinfo: '../../js/modules/sinfo/sinfo'
  },
  shim: {
    jquery: {
      exports: '$'
    },
    'jquery-tablesorter': {
      deps: [ 'jquery' ]
    },
    'jquery-flot': {
      deps: [ 'jquery' ]
    },
    'jquery-flot-pie': {
      deps: [ 'jquery', 'jquery-flot' ]
    },
    handlebars: {
      exports: 'Handlebars'
    },
    bootstrap: {
      deps: [ 'jquery' ]
    },
    'bootstrap-typeahead': {
      deps: [ 'jquery' ],
      init: function($) {
        return require.s.contexts._.registry['typeahead.js'].factory($);
      }
    },
    'bootstrap-tagsinput': {
      deps: [ 'jquery', 'bootstrap', 'bootstrap-typeahead' ]
    }
  }
});

if (isIE) {
  require([ 'xdomain' ], function(xdomain) { // eslint-disable-line global-require
    var index, slaves = {};

    for (index in window.clusters) {
      slaves[window.clusters[index].api.url] = window.clusters[index].api.path + '/proxy';
    }
    xdomain.slaves(slaves);
  });
}

require([
  'jquery',
  'page-utils',
  'text!/slurm-web-conf/config.json',
  'token-utils',
  'user-utils',
  'login',
  'navbar',
  'clusters',
  'jobs',
  'racks',
  'jobs-map',
  'qos',
  'partitions',
  'reservations',
  '3d-view',
  'gantt',
  'topology',
  'ajax-utils'
], function($, Page, config, token, user, Login, Navbar, Clusters, Jobs, Racks, JobsMap, QOS, Partitions, Reservations, D3View, Gantt, Topology, ajaxUtils) {
  var clusters = null,
    page = new Page(),
    navbar = null;

  config = JSON.parse(config);
  clusters = new Clusters(config);
  clusters.init();

  String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
  }
  //define loader
  var $loader = $('#loader').hide();
  //show loader when page is loading
  $(document).ajaxStart(function(){
    $loader.show();
  }) //hide when stop loading
  .ajaxStop(function(){
    $loader.hide();
  });

  $(document).on('loadPage', function(e, options) {
    e.stopPropagation();
    $(document).trigger('destroyNavbar');

    navbar = new Navbar(options.config);
    navbar.init();

    $('title').html(options.config.cluster.name.capitalizeFirstLetter() + '\'s HPC Dashboard');
    $(document).trigger('show', { page: config.STARTPAGE });
  });

  $(document).on('logout', function(e, onlyCurrentCluster) {
    var cluster;

    e.preventDefault();

    function logout(cluster) {
      token.removeToken(cluster);
      user.removeUser(cluster);
    }

    if (!config.AUTOLOGIN || onlyCurrentCluster) {
      // clear authentication on current cluster
      logout(config.cluster);
    } else {
      // clear authentication on all clusters
      for (cluster in window.clusters) {
        logout(window.clusters[cluster]);
      }
    }

    $(document).trigger('show', { page: config.cluster.authentication.enabled ? 'login' : config.STARTPAGE });
  });

  $(document).on('show', function(e, options) {
    // check if the wanted page is accessible for the current user
    var nextPage = options.page !== 'login' &&
      navbar.availableViews.filter(function(view) {
        return view.id === options.page;
      }).length === 0 ? navbar.availableViews[0].id : options.page;

    e.stopPropagation();

    page.destroy(true);
    $('#main > div').not('#flash').remove();
    page = new Page();

    if ($('#flash.display').length) {
      $('#flash').show().removeClass('display');
    } else {
      $('#flash').hide().find('.alert').empty();
    }

    switch (nextPage) {
    case 'login':
      page = new Login(config);
      break;
    case 'jobs':
      if (options.filter) {
        page = new Jobs(config, options.filter);
      } else {
        page = new Jobs(config, null);
      }
      break;
    case 'jobsmap':
      page = new JobsMap(config);
      break;
    case 'partitions':
      page = new Partitions(config);
      break;
    case 'reservations':
      page = new Reservations(config);
      break;
    case 'qos':
      page = new QOS(config);
      break;
    case 'racks':
      page = new Racks(config);
      break;
    case '3dview':
      page = new D3View(config);
      break;
    case 'gantt':
      page = new Gantt(config);
      break;
    case 'topology':
      page = new Topology(config);
      break;
    case 'sinfo':
      page = new Sinfo(config);
      break;
    }

    if (page.hasOwnProperty('init')) {
      page.init();
    }

    if (page.hasOwnProperty('refresh')) {
      page.refresh();
    }

    if (page.hasOwnProperty('stopRefresh') && config.REFRESHCHECKBOX) {
      $("#refreshCheckbox").off("change"); // don't stack events
      $("#refreshCheckbox").change(function() {
        if (this.checked) {
          page.refresh();
        } else {
          page.stopRefresh();
        }
        document.cookie = 'dashboardRefresh='+this.checked+'; max-age=31536000';
      });
      var cookieCheck = document.cookie.replace(/(?:(?:^|.*;\s*)dashboardRefresh\s*\=\s*([^;]*).*$)|^.*$/, "$1") !== "false";
      $("#refreshCheckbox").prop('checked', cookieCheck);
      if (!cookieCheck) {
        page.stopRefresh();
      }
      $("#refreshCheckboxContainer").show();
    } else {
      $("#refreshCheckboxContainer").hide();
    }

  });

  $(window).resize(function() {
    $('body>.container-fluid').css({ 'margin-top': $('nav').height() + 'px' });
  });
});
