#!/bin/bash -l

ROLEOUTPUTFILE="${WORKSPACE}/credentials.txt"
ACCOUNT="860429940966"
REGION="us-west-2"
set +x

# Get temporary credentials in order to create stack
aws sts assume-role --role-arn=arn:aws:iam::${ACCOUNT}:role/User --role-session-name="userRole" --region ${REGION} > ${ROLEOUTPUTFILE}
export AWS_SECRET_ACCESS_KEY=`grep SecretAccessKey $ROLEOUTPUTFILE |cut -d"\"" -f4`
export AWS_SESSION_TOKEN=`grep SessionToken $ROLEOUTPUTFILE |cut -d"\"" -f4`
export AWS_ACCESS_KEY_ID=`grep AccessKeyId $ROLEOUTPUTFILE |cut -d"\"" -f4`
echo "AWS security tokens obtained."

echo && echo "Login to Docker ECR Registry"
eval $(aws ecr get-login --no-include-email --region $REGION)
set -x

if [ -f "package.json" ]; then
  BASEVER=`grep "version" package.json |cut -d'"' -f4`
else
  BASEVER=1.0
fi

# create a unique build number with total revisions and hash
# return a count of total revisions formatted as '0001'
BUILDID=`git rev-list HEAD | wc -l | sed -e 's/ *//g' | xargs -n1 printf %04d`

# return the SHA hash for this revision
echo && echo "Create Hash Value for Unique Build ID"
HASHVER=`git rev-parse --short HEAD`

# combine revision count and hash to create unique package version
export PACKAGE_VERSION="${BASEVER}.${BUILDID}.${HASHVER}"
echo "Package Version: $PACKAGE_VERSION"
export IMAGE=dfimage

echo && echo "Building and Taging Docker Container."
docker build --no-cache --rm -t $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$IMAGE:$PACKAGE_VERSION -t $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$IMAGE:latest .

echo && echo "Pushing Container to AWS ECR."
docker push $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$IMAGE:$PACKAGE_VERSION
docker push $ACCOUNT.dkr.ecr.$REGION.amazonaws.com/$IMAGE:latest
