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

define([
  'jquery',
  'token-utils'
], function ($, tokenUtils) {
  return {
    getJobs: function (config) {
      var slurmJobs = null;
      var options = {
        type: 'POST',
        dataType: 'json',
        async: false,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        data: JSON.stringify({
          token: tokenUtils.getToken(config.cluster)
        })
      };

      $.ajax(config.cluster.api.url + config.cluster.api.path + '/jobs', options)
        .success(function (jobs) {
          slurmJobs = jobs;
        })
        .error(function () {
          $(document).trigger('show', { page: 'login' });
        });

      return slurmJobs;
    },
    buildAllocatedCPUs: function (jobs) {
      var allocatedCPUs = {};
      var nodesCPUs = null;
      var job;
      var node;

      for (job in jobs) {
        if (jobs.hasOwnProperty(job) && jobs[job].job_state === 'RUNNING') {
          nodesCPUs = jobs[job].cpus_allocated;
          for (node in nodesCPUs) {
            if (nodesCPUs.hasOwnProperty(node)) {
              if (!allocatedCPUs.hasOwnProperty(node)) {
                allocatedCPUs[node] = {};
              }
              allocatedCPUs[node][job] = nodesCPUs[node];
            }
          }
        }
      }

      return allocatedCPUs;
    }
  };
});
