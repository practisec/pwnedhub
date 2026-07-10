#!/bin/sh

PYTEST_ARGS="${@:--v}"

run_tests() {
    service=$1
    test_dir=$2
    echo ""
    echo "================================================================"
    echo " Running $test_dir tests in '$service' container"
    echo "================================================================"
    # Run in the live container, which already has the service's deps and pytest
    # installed by its command: at startup. Requires the stack to be up.
    docker compose exec -e CONFIG=Test "$service" \
        python3 -m pytest $test_dir $PYTEST_ARGS
    return $?
}

failed=0

run_tests app    tests/pwnedhub  || failed=1
run_tests api    tests/pwnedapi  || failed=1
run_tests sso    tests/pwnedsso  || failed=1
run_tests admin  tests/pwnedadmin || failed=1

echo ""
echo "================================================================"
if [ $failed -eq 0 ]; then
    echo " All test suites passed."
else
    echo " Some test suites had failures."
fi
echo "================================================================"

exit $failed
