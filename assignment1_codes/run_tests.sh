#! /bin/bash
export GOPATH=$(pwd)
grade=0
check_code_part_II=false
check_code_part_III=false

cd src/main
echo "Grading part I:"
go run wc.go master kjv12.txt sequential > partI.out
dos2unix mrtmp.kjv12.txt
sort -n -k2 mrtmp.kjv12.txt | tail -10 | diff - mr-testout.txt > diff.out
if [ -s diff.out ]
then
echo "FAILED TEST FOR PART I! Output should be as in mr-testout.txt. Your output differs as follows (from diff.out):"
  cat diff.out
else
  echo "PASSED TEST FOR PART I!"
  ((grade+=20))
fi
rm mrtmp.*
echo "----------------------------------------"

cd ../mapreduce
cp ../../../../../grading_test_test.go test_test.go

echo "Grading part II:"
count_basic=0
for i in {1..5}
do
    echo "Running TestBasic: #$i"
    go test -run TestBasic > test_basic_$i.out
    tail -5 test_basic_$i.out | grep -Fxq "JejjEOkcQT...TestBasicPassed...hdmDJlqpn3"
    if [ $? -eq 0 ]; then
        ((count_basic+=1))
    else
        echo "TestBasic FAILED!"
    fi
done

echo "# of times TestBasic passed: "$count_basic
if [ $count_basic -eq 5 ]; then
    ((grade+=50))
elif [ $count_basic -gt 0 ]; then
    ((grade+=35))
else
    echo "CHECK THE CODE!"
    check_code_part_II=true
fi
unset count_basic

echo "----------------------------------------"
echo "Grading part III:"
count_onefail=0
for i in {1..5}
do
    echo "Running TestOneFailure: #$i"
    go test -run TestOneFailure > test_onefail_$i.out
    tail -5 test_onefail_$i.out | grep -Fxq "EesIBVG3Rl...OneFailurePassed...AtTkChNYgK"
    if [ $? -eq 0 ]; then
        ((count_onefail+=1))
    else
        echo "TestOneFailure FAILED!"
    fi
done

echo "# of times TestOneFailure passed: "$count_onefail
if [ $count_onefail -eq 5 ]; then
    ((grade+=15))
elif [ $count_onefail -gt 0 ]; then
    ((grade+=10))
else
    echo "CHECK THE CODE!"
    check_code_part_III=true
fi
unset count_onefail

echo "----------------------------------------"
count_manyfail=0
for i in {1..5}
do
    echo "Running TestManyFailures: #$i"
    go test -run TestManyFailures > test_manyfail_$i.out
    tail -5 test_manyfail_$i.out | grep -Fxq "KaC0KFyCvW...ManyFailuresPassed...S9g2A1YfYk"
    if [ $? -eq 0 ]; then
        ((count_manyfail+=1))
    else
        echo "TestManyFailures FAILED!"
    fi
done

echo "# of times TestManyFailures passed: "$count_manyfail
if [ $count_manyfail -eq 5 ]; then
    ((grade+=15))
elif [ $count_manyfail -gt 0 ]; then
    ((grade+=10))
else
    echo "CHECK THE CODE!"
    check_code_part_III=true
fi
unset count_manyfail

# rm mrtmp.*
echo "----------------------------------------"
echo "Check code for part II: "$check_code_part_II
echo "Check code for part III: "$check_code_part_III
echo "Grade: "$grade
