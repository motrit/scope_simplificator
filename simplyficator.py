#!/usr/bin/python3
#-*- coding: utf-8 -*-

import dns.resolver

connections = dict()

class Record(object):
    def __init__(self, domain=None, cname_for=None, cname=None):
        self.domain = domain
        self.cname = cname 
        self.cname_for = [cname_for] if cname_for else []

def get_cname_chain(source_domain):
    domain = source_domain
    while True:
        try :
            answer = dns.resolver.query(domain, "CNAME")
        except dns.resolver.NoAnswer :
            answer = []
        if len(answer) < 1 :
            return
        elif len(answer) > 1 :
            print ("#INFO# Multiple CNAME records found - needs improvement", domain)
            return
        else :
            if domain not in connections :
                connections[domain] = str(answer[0])
                domain = str(answer[0])
            elif connections[domain] != str(answer[0]):
                print ("#INFO# Multiple CNAME records found from another source", domain)
                return 

def read_hosts(filename):
    hosts = []
    for host in open(filename).readlines():
        hosts.append(host.replace('\n',''))
    return hosts

def print_record_chain(record, offset = 0):
    print ("|   "*(offset-1) + "|    " * (1 if offset else 0))
    print ("|   "*(offset-1) + "|--->" * (1 if offset else 0), record.domain)
    if record.cname_for :
        for child_index in range(len(record.cname_for)):
            print_record_chain(record.cname_for[child_index], offset + 1)




def main():
    filename = "scope1.txt"
    hosts = read_hosts(filename)
    root = Record()
    existing_domains = dict()
    for item in hosts :
        get_cname_chain(item)

    for host, cname in connections.items() :
        
        if host not in existing_domains:
            node_host = Record(domain = host)
            existing_domains[host] = node_host
        else:
            node_host = existing_domains[host]
        if cname not in existing_domains:
            node_cname = Record(domain = cname)
            existing_domains[cname] = node_cname
        else:
            node_cname = existing_domains[cname]
        node_host.cname = node_cname
        node_cname.cname_for.append(node_host)
    for item in existing_domains:
        if existing_domains[item].cname == None :
            print_record_chain(existing_domains[item])

if __name__ == "__main__" :
    main()
