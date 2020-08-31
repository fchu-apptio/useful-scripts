#!/bin/bash

function usage() {
    echo "Usage: troublehshoot.sh [-v]"
    echo
    echo " -v Increase logging"
}

while getopts "v" opt; do
  case "$opt" in
    v)
        VERBOSE=1
        ;;
   esac
done

# Initialize the error count
ERROR_COUNT=0
WARNING_COUNT=0

# Identify the machine that is running
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     
        echo "[INFO] Using Linux"
        USING_LINUX=1
        ;;
    Darwin*)    
        echo "[INFO] Using Mac"
        USING_MAC=1
        ;;
    *)
        echo "[ERROR] Unrecongized operating system, ${unameOut}"
        exit 1
        ;;
esac

# Display docker processes
if [ $VERBOSE ]
then
    docker ps
fi

# Validate that mysql is running
echo "[INFO] checking docker processes to find mysql"
ROUTER_MYSQL_CONT=$(docker ps --quiet --filter=name="router_mysql_1" | head -n 1);
echo "[INFO] USING ROUTER_MYSQL_CONT: ${ROUTER_MYSQL_CONT}"

echo "[INFO] checking docker processes to find mysql"
MYSQL_CONT=$(docker ps --quiet --filter=name="mysql_mysql_1" | head -n 1);
echo "[INFO] USING MYSQL_CONT: ${MYSQL_CONT}"

if [ ${ROUTER_MYSQL_CONT} ];
then
    echo "[INFO] Mysql is running"
    ROUTER_MYSQL_CMD="docker exec -it ${ROUTER_MYSQL_CONT} mysql"
else
    echo "[ERROR] missing router_mysql, exiting application. You must either run mysql locally or in docker"
    exit 1
fi

if [ ${MYSQL_CONT} ];
then
    echo "[INFO] Mysql is running"
    MYSQL_CMD="docker exec -it ${MYSQL_CONT} mysql"
else
    echo "[ERROR] missing mysql_mysql, exiting application. You must either run mysql locally or in docker"
    exit 1
fi

# Validate that redis is running
echo "[INFO] checking docker processes to find redis"
REDIS_CONT=$(docker ps --quiet --filter=name="docker_redis_1");
echo "[INFO] REDIS_CONT: ${REDIS_CONT}"
if [ ${REDIS_CONT} ];
then
   echo "[INFO] Redis is running"
else
   echo "[ERROR] Redis is not running"
   echo "[RECOMMENDATION] Start redis in docker (docker start docker_redis_1)"
   echo "[RECOMMENDATION] https://confluence.apptio.com/display/rnd/Setting+up+Router"
   ERROR_COUNT=$((ERROR_COUNT+1))
fi

# Validate that router is running
echo "[INFO] Router healthcheck on localhost:9050..."
if $( curl --connect-timeout 5 'localhost:9050/sf/healthcheck' | grep -q 'Healthy' );
then
   echo "[INFO] Router is running"
else
   echo "[ERROR] Router is not running"
   echo "[RECOMMENDATION] Start router in docker (docker start docker_router_1)"
   echo "[RECOMMENDATION] https://confluence.apptio.com/display/rnd/Setting+up+Router"
   ERROR_COUNT=$((ERROR_COUNT+1))
fi

# Validate that bff is running
echo "[INFO] checking for bff on localhost:9080..."
if $( curl --connect-timeout 5 localhost:9080/healthcheck | grep -q 'OK' ); 
then
   echo "[INFO] BFF is running"
else
   echo "[ERROR] BFF is not running"
   echo "[RECOMMENDATION] Run BFF either in docker, intellij, or in terminal"
   echo "[RECOMMENDATION] https://confluence.apptio.com/pages/viewpage.action?pageId=111414527"
   ERROR_COUNT=$((ERROR_COUNT+1))
fi

# Validate that server is running
echo "[INFO] checking for server on localhost:9180..."
if $( curl --connect-timeout 5 localhost:9180/biit/health | grep -q 'OK' ); 
then
   echo "[INFO] BIIT Server is running"
else
   echo "[ERROR] BIIT Server is not running"
   echo "[RECOMMENDATION] Run BIIT either in docker, intellij, or in terminal"
   echo "[RECOMMENDATION] https://confluence.apptio.com/pages/viewpage.action?pageId=111414527"
   ERROR_COUNT=$((ERROR_COUNT+1))
fi

# Check docker ps to identify if BFF is running as a docker image
BFF_CONT=$( docker ps --quiet --filter=name="studio_bff" );
echo "[INFO] BFF_CONT: ${BFF_CONT}"

# Check docker ps to identify if Router is running as a docker image
ROUTER_CONT=$( docker ps --quiet --filter=name="docker_router_1" )
echo "[INFO] ROUTER_CONT: ${ROUTER_CONT}"

# Print out all joined tables for debugging
echo "[INFO] displaying relevant locator db columns"
PRINT_ALL_DB="SELECT app.Name, app.Pattern, ver.ElbAddress, 
enver.VersionBuildNumber, enveres.Location BiitAddress, env.FullyQualifiedEnvironmentName
FROM locator.Application app 
JOIN locator.Version ver ON app.Id = ver.ApplicationId 
JOIN locator.EnvironmentVersion enver ON app.Id = enver.ApplicationId 
JOIN locator.EnvironmentVersionResource enveres ON enveres.EnvironmentVersionId = enver.Id
JOIN locator.Environment env ON env.Id = enver.EnvironmentId"
echo "${PRINT_ALL_DB}"
${ROUTER_MYSQL_CMD} -u biit -pbiit --protocol=tcp -e "${PRINT_ALL_DB}"
if [ "$MYSQL_CMD" = "mysql" ]
then
    echo "[WARN] using local mysql command, sometimes this can run slow"
fi
if [ $? -ne "0" ]; 
then
    echo "[ERROR] Error running mysql command"
    echo "[RECOMMENDATION] Your locator database might not exist"
    echo "[RECOMMENDATION] 'docker restart docker_router_1' to create it"
    ERROR_COUNT=$((ERROR_COUNT+1))
fi

# Validating bff address
echo "[INFO] Processing locator.Version.ElbAddress..."
PRINT_BFF_ADDRESS="SELECT ver.ElbAddress FROM locator.Version ver"
CONTAINS_LINES=0
while read -r line;
do
    CONTAINS_LINES=1

    if [[ $line = "localhost:9002" || $line = "host.docker.internal:9002" || $line = "shell-studio.apps.dapt.to"  ]];
    then
        continue
    fi

    echo $line | cat -v
    if ( [ $USING_LINUX ] || [ -z $ROUTER_CONT ] );
    then
        if [ $line != "localhost:9080" ];
        then
            echo "[ERROR] locator.Version.ElbAddress should be localhost:9080, found [$line]"
            echo "[INFO] This address is used in linux or for macs when running router in intellij"
            echo "[RECOMMENDATION] Change the locator.Version.ElbAddress to localhost:9080"
            echo "[RECOMMENDATION] Check the confluence for details https://confluence.apptio.com/display/rnd/Setting+up+Router"
            ERROR_COUNT=$((ERROR_COUNT+1))
        fi
    else
        if [ $line != "host.docker.internal:9080" ];
        then
            echo "[ERROR] locator.Version.ElbAddress should be host.docker.internal:9080, found [$line]"
            echo "[INFO] This address is used for macs when running router in a docker container"
            echo "[RECOMMENDATION] Change the locator.Version.ElbAddress to host.docker.internal:9080"
            echo "[RECOMMENDATION] Check the confluence for details https://confluence.apptio.com/display/rnd/Setting+up+Router"
            ERROR_COUNT=$((ERROR_COUNT+1))
        fi
    fi
done < <( $ROUTER_MYSQL_CMD -u biit -pbiit --protocol=tcp -N -s -e "${PRINT_BFF_ADDRESS}" | grep -v "Warning" | tr -d '\r'  )
if [ $CONTAINS_LINES -ne 1 ]
then
    echo "[ERROR] Did not find any rows in locator.Version"
    echo "[RECOMMENDATION] Please run ./registerRouter script"
    echo "[RECOMMENDATION] Check the confluence for details https://confluence.apptio.com/display/rnd/Setting+up+Router"
    ERROR_COUNT=$((ERROR_COUNT+1))
fi

# Validating biit address
echo "[INFO] Processing locator.EnvironmentVersionResource.Location..."
PRINT_BFF_ADDRESS="SELECT enveres.Location FROM locator.EnvironmentVersionResource enveres"
CONTAINS_LINES=0
while read -r line;
do
    CONTAINS_LINES=1
    echo $line | cat -v
    if ( [ $USING_LINUX ] || [ -z $BFF_CONT ] );
    then
        if [ $line != "localhost:9180" ];
        then
            echo "[ERROR] locator.EnvironmentVersionResource.Location should be localhost:9180, found [$line]"
            echo "[INFO] This address is used for linux or for macs when running bff in intellij"
            echo "[RECOMMENDATION] Change the locator.EnvironmentVersionResource.Location to localhost:9180"
            echo "[RECOMMENDATION] Check the confluence for details https://confluence.apptio.com/display/rnd/Setting+up+Router"
            ERROR_COUNT=$((ERROR_COUNT+1))
        fi
    else
        if [ $line != "host.docker.internal:9180" ];
        then
            echo "[ERROR] locator.EnvironmentVersionResource.Location should be host.docker.internal:9180, found [$line]"
            echo "[INFO] This address is used for macs when running bff in a docker container"
            echo "[RECOMMENDATION] Change the locator.EnvironmentVersionResource.Location to host.docker.internal:9180"
            echo "[RECOMMENDATION] Check the confluence for details https://confluence.apptio.com/display/rnd/Setting+up+Router"
            ERROR_COUNT=$((ERROR_COUNT+1))
        fi
    fi
done < <( $ROUTER_MYSQL_CMD -u biit -pbiit --protocol=tcp -N -s -e "${PRINT_BFF_ADDRESS}" | grep -v "Warning" | tr -d '\r'  )
if [ $CONTAINS_LINES -ne 1 ]
then
    echo "[ERROR] Did not find any rows in locator.EnvironmentVersionResource"
    echo "[RECOMMENDATION] Please run ./registerRouter script"
    echo "[RECOMMENDATION] Check the confluence for details https://confluence.apptio.com/display/rnd/Setting+up+Router"
    ERROR_COUNT=$((ERROR_COUNT+1))
fi

# Check the following select in the database to ensure that Config is filled
if [ $VERBOSE ]
then
    $MYSQL_CMD -u biit -pbiit --protocol=tcp -e "SELECT * FROM biit_db.Config"
fi

# Check that we have a global application key
echo "[INFO] Validating Config.ApplicationId..."
APP_ID=$( $MYSQL_CMD -u biit -pbiit --protocol=tcp -N -s -e "SELECT configValue FROM biit_db.Config WHERE configKey='apptio.auth.frontdoor.application.id'" | grep -v "Warning" | tr -d '\r' )
echo $APP_ID | cat -v
if [ -z $APP_ID ];
then
    echo "[ERROR] Application Id is missing in biit_db.Config"
    echo "[RECOMMENDATION] Did you forget to restore frontdoor backups? "
    echo "[RECOMMENDATION] Otherwise you will need to Provision Frontdoor"
    echo "[RECOMMENDATION] https://confluence.apptio.com/display/rnd/Set+Up+MySQL+Docker+Container+and+Provision+FrontDoor#SetUpMySQLDockerContainerandProvisionFrontDoor-ProvisionFrontdoor"
    ERROR_COUNT=$((ERROR_COUNT+1))
fi

# Check that we have a environment id for each domain
echo "[INFO] Validating Config.EnvironmentIds..."
CONTAINS_LINES=0
while read -r line;
do
    CONTAINS_LINES=1
    echo $line | cat -v
    if [ -z $line ]
    then
        echo "[ERROR] Environment Id is missing in biit_db.Config"
        echo "[RECOMMENDATION] Did you forget to restore frontdoor backups? "
        echo "[RECOMMENDATION] Otherwise you will need to Provision Frontdoor"
        echo "[RECOMMENDATION] https://confluence.apptio.com/display/rnd/Set+Up+MySQL+Docker+Container+and+Provision+FrontDoor#SetUpMySQLDockerContainerandProvisionFrontDoor-ProvisionFrontdoor"
        ERROR_COUNT=$((ERROR_COUNT+1))
    fi
done < <( $MYSQL_CMD -u biit -pbiit --protocol=tcp -N -s -e "SELECT configValue FROM biit_db.Config WHERE configKey='apptio.frontdoor.domain.environment.id'" | grep -v "Warning" | tr -d '\r'  )
if [ $CONTAINS_LINES -ne 1 ]
then
    echo "[ERROR] Did not find EnvironmentId in biit_db.Config"
    echo "[RECOMMENDATION] Something is corrupted in your mysql database. Might need to delete the volume and recreate"
    echo "[RECOMMENDATION] https://confluence.apptio.com/display/rnd/Set+Up+MySQL+Docker+Container+and+Provision+FrontDoor"
    ERROR_COUNT=$((ERROR_COUNT+1))
fi

##
## TODO: Check frontdoor to see the environment id and validate the biit_db.Config table
## TODO: If we know the frontdoor environment name we can validate the locator.Environment.FullyQualifiedEnvironmentName
## When we have time and are in need of this environment validation 
## we can make this a python script that uses the following 
## https://confluence.apptio.com/display/rnd/Frontdoor+Python+Tools
##

if [ $WARNING_COUNT -ge 1 ]
then
    echo "***WARNING*** ${WARNING_COUNT} warning(s) found! please search the output logs for [WARN] and check their recommendations"
fi

echo "errors: ${ERROR_COUNT}"
if [ $ERROR_COUNT -ge 1 ]
then
    echo
    echo "***ERROR*** ${ERROR_COUNT} error(s) found! please search the output logs for [ERROR] and check their recommendations"
    exit 1
else
    echo
    echo "***SUCCESS*** No errors were found during troubleshooting"
    echo "If you are still experiencing problems try running in an icognito browser."
    echo "Follow logs in docker containers via 'docker logs -f <container_name>'"
    echo "If all else fails, please run this script again with -v and post any logs found in #bff-help"
    echo "I recommend posting as an attachment, so the channel is not spammed unecessarily"
fi
