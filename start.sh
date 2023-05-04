
#/bin/bash
function update_env_variable {
  local compose_file="$1"
  local search_key="$2"
  local search_value="$3"
  local env_key="${4:-REDIS_HOST}"
  local env_file=$5

  # Find the container name from docker-compose.yml
  compose_value=$(grep -A 1 "$search_key" "$compose_file" | grep "$search_value" | awk '{print $2}')

  # Read the value from .env
  env_value=$(grep "$env_key" $env_file | cut -d'=' -f2)


  if [[ "$compose_value" == *":"* ]]; then
    compose_value=${compose_value#*:}
  else
    compose_value="$compose_value"
  fi
  

  # Check if the value matches the container name
  if [ "$compose_value" != "$env_value" ]; then
    # Update the value in the .env file
    sed -i '' -e "s/$env_key=$env_value/$env_key=$compose_value/g" $env_file
    echo "Updated $env_key in $env_file to $compose_value."
  else
    echo "$env_key in $env_file already matches the container name."
  fi
}

# Usage: update_env_variable <compose_file> <search_key> [<env_key>]
# Example: update_env_variable "docker-compose.yml" "Redis" "REDIS_HOST"

envfiles=(".env.receiver" ".env.sender")
for envfile in "${envfiles[@]}"

do
    if [ -f "$envfile" ]; then
         echo "$envfile found."
    else
        echo "Creating $FILE file"
         cp .env.example $envfile
    fi
  # find the second part of the envfile name
  # e.g. .env.receiver -> receiver
  envfile_name=$(echo "$envfile" | cut -d'.' -f3)
  dockerfile_name="docker-compose.$envfile_name.yml"
  update_env_variable $dockerfile_name "container_name" "redis" "REDIS_HOST" $envfile 
  update_env_variable $dockerfile_name "port" "6379" "REDIS_PORT" $envfile
done


#create network
docker network create osnap
if [ $? -eq 0 ]
    then
        echo "Network created"
else
   echo "Network already exists"
    fi

#build images
docker compose -f docker-compose.sender.yml -f docker-compose.receiver.yml up

