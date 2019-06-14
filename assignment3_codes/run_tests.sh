#! /usr/local/bin/bash
export GOPATH=$(pwd)

cd src/paxos/
cp ../../../../paxos_test.go test_test.go
paxos_tests=(TestBasic TestDeaf TestForget TestManyForget TestForgetMem TestDoneMax TestRPCCount TestMany TestOld TestManyUnreliable TestPartition TestLots)
# echo "Running Part I (paxos) tests:"
for test_name in "${paxos_tests[@]}"
do
    for i in {1..5}
    do
        # echo "Running $test_name: round #$i"
        go test -run $test_name > $test_name\_$i.out
    done
    echo "--------------------Done w. PartI-$test_name--------------------";
done

cd ../kvpaxos
cp ../../../../kvpaxos_test.go test_test.go
kvpaxos_tests=(TestBasic TestDone TestPartition TestUnreliable TestHole TestManyPartition)
# echo "Running Part II (kvpaxos) tests:"
for test_name in "${kvpaxos_tests[@]}"
do
    for i in {1..5}
    do
        # echo "Running $test_name: round #$i"
        go test -run $test_name > $test_name\_$i.out
    done
    # echo "--------------------Done w. PartII-$test_name--------------------";
done
