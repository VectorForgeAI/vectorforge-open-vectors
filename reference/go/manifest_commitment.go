// manifest_commitment reference implementation (Go)
//
// Merkle root with SHA3-512 and duplicate-last padding.

package main

import (
	"crypto/sha3"
	"encoding/base64"
	"fmt"
	"os"
)

func merkleRoot(leaves [][]byte) []byte {
	if len(leaves) == 0 {
		h := sha3.Sum512([]byte{})
		return h[:]
	}
	level := leaves
	for len(level) > 1 {
		var next [][]byte
		for i := 0; i < len(level); i += 2 {
			left := level[i]
			right := left
			if i+1 < len(level) {
				right = level[i+1]
			}
			h := sha3.Sum512(append(left, right...))
			next = append(next, h[:])
		}
		level = next
	}
	return level[0]
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("usage: manifest_commitment <base64leaf1> <base64leaf2> ...")
		os.Exit(2)
	}
	var leaves [][]byte
	for _, a := range os.Args[1:] {
		b, err := base64.StdEncoding.DecodeString(a)
		if err != nil {
			fmt.Println("decode error:", err)
			os.Exit(1)
		}
		leaves = append(leaves, b)
	}
	root := merkleRoot(leaves)
	fmt.Println(base64.StdEncoding.EncodeToString(root))
}
