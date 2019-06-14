#! /bin/bash
export GOPATH=$(pwd)

cd src/shardmaster/
cp ../../../../shardmaster_test.go test_test.go
shardmaster_tests=(TestBasic TestUnreliable TestFreshQuery)
echo "Running Part I (shardmaster) tests:"
for test_name in "${shardmaster_tests[@]}"
do
    for i in {1..5}
    do
        echo "Running $test_name: round #$i"
        go test -run $test_name > $test_name\_$i.out
    done
    echo "--------------------Done w. PartI-$test_name--------------------";
done

cd ../shardkv
cp ../../../../shardkv_test.go test_test.go
shardkv_tests=(TestBasic TestMove TestLimp TestConcurrent TestConcurrentUnreliable)
echo "Running Part II (shardkv) tests:"
for test_name in "${shardkv_tests[@]}"
do
    for i in {1..5}
    do
        echo "Running $test_name: round #$i"
        go test -run $test_name > $test_name\_$i.out
    done
    echo "--------------------Done w. PartII-$test_name--------------------";
done

