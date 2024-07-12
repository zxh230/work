#!/bin/bash
/usr/sbin/ip netns add namespace1
/usr/sbin/ip netns add namespace2
/usr/sbin/ip netns exec namespace1 ip link set dev lo up
/usr/sbin/ip netns exec namespace2 ip link set dev lo up
/usr/sbin/ip link add veth0 type veth peer name veth1
/usr/sbin/ip link add veth2 type veth peer name veth3
/usr/sbin/ip link set veth1 netns namespace1
/usr/sbin/ip link set veth3 netns namespace2
/usr/sbin/ifconfig veth0 5.5.5.1/24
/usr/sbin/ifconfig veth2 15.15.15.1/24
/usr/sbin/ip netns exec namespace1 ifconfig veth1 5.5.5.2/24
/usr/sbin/ip netns exec namespace2 ifconfig veth3 15.15.15.2/24
/usr/sbin/ip netns exec namespace1 route add defaule gw 5.5.5.1
/usr/sbin/ip netns exec namespace1 route add default gw 5.5.5.1
/usr/sbin/ip netns exec namespace2 route add default gw 15.15.15.1
