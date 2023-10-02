#!/usr/bin/env bash

# Default parameter values
fixtures="fixtures"
repeat=1

# Process named parameters
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--fixtures_dir)
            fixtures="$2"
            shift ;;
        -r|--repeat)
            repeat="$2"
            shift ;;
        *)
            # Unknown option, print usage and exit
            echo "Unknown option: $1"
            exit 1 ;;
    esac
    shift
done

echo "Fixtures directory: $fixtures"
echo "Number of generatin repetitions for each application description: $repeat"
set -e
set -x

cd $fixtures
python -c 'from faststream_gen._testing import benchmark; benchmark.app([".", "--repeat", "'$repeat'"])'

