 # Docker Swarm Management for Heavy Forwarders
 
 ## Introduction
 
 ### Problem
 
 Managing "do everything" heavy forwarders is tedious: dependencies, deployment servers, conflicting configurations,
 failover.
 
 This can be easier.
 
 ### Solution
 
 Containers allow us to independently manage one input, or group a handful of similar inputs without additional
 hardware, real or virtual.  They can also be shipped to another infrastructure without worrying about the other admins
 changing anything.
 
 Docker Swarm enables scaling and failover for these containers.  Sprinkle in some persistent storage and your heavy
 forwarders are now significantly more resilient than before.
 
 ## Basic Process
 
 These playbooks provide you with this path:
 
 * Define your heavy forwarder image
   * Operating System
   * Splunk Version
   * TAs (or other configs) to install via local file, templates, git repositories, etc.
   * Healthcheck index/sourcetype and expected event time period
   * Volumes for persistent storage
   
* Build your image, along with some convenient variants

   * Primary image
      * Intended to be deployed to swarm
      * Disables indexes, splunkweb
      * Configures license master
      
   * Standalone image
      * Eases development efforts prior to deploying to swarm
      * Leaves splunkweb enabled
      * Allows simple index creation
   
* Push your image to a registry

* Deploy a service using your image

## Examples

### Simplest image definition