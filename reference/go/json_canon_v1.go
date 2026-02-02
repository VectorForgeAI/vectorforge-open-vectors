// json_canon_v1 reference implementation (Go)
//
// Purpose:
// - RFC 8785-inspired canonicalization
// - Deviations: no floats, no duplicate keys, safe integer range
//
// Notes:
// - This file is intentionally small and readable. It prioritizes correctness over speed.
// - For production, consider a hardened parser with streaming support.

package main

import (
	"bytes"
	"crypto/sha3"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"math"
	"os"
	"sort"
)

const SAFE_INT_MAX = float64((1 << 53) - 1)
const SAFE_INT_MIN = -SAFE_INT_MAX

type Value interface{}

func parseJSONStrictNoFloats(input []byte) (Value, error) {
	dec := json.NewDecoder(bytes.NewReader(input))
	dec.UseNumber()

	val, err := parseValue(dec)
	if err != nil {
		return nil, err
	}

	// Ensure no extra tokens
	if dec.More() {
		return nil, errors.New("INVALID_JSON: extra tokens")
	}
	return val, nil
}

func parseValue(dec *json.Decoder) (Value, error) {
	tok, err := dec.Token()
	if err != nil {
		return nil, fmt.Errorf("INVALID_JSON:%w", err)
	}

	switch t := tok.(type) {
	case json.Delim:
		if t == '{' {
			obj := map[string]Value{}
			seen := map[string]bool{}
			for dec.More() {
				ktok, err := dec.Token()
				if err != nil {
					return nil, fmt.Errorf("INVALID_JSON:%w", err)
				}
				k, ok := ktok.(string)
				if !ok {
					return nil, errors.New("INVALID_JSON: object key not string")
				}
				if seen[k] {
					return nil, fmt.Errorf("DUPLICATE_KEY:%s", k)
				}
				seen[k] = true
				v, err := parseValue(dec)
				if err != nil {
					return nil, err
				}
				obj[k] = v
			}
			// consume '}'
			end, err := dec.Token()
			if err != nil {
				return nil, fmt.Errorf("INVALID_JSON:%w", err)
			}
			if end.(json.Delim) != '}' {
				return nil, errors.New("INVALID_JSON: expected '}'")
			}
			return obj, nil
		}
		if t == '[' {
			arr := []Value{}
			for dec.More() {
				v, err := parseValue(dec)
				if err != nil {
					return nil, err
				}
				arr = append(arr, v)
			}
			// consume ']'
			end, err := dec.Token()
			if err != nil {
				return nil, fmt.Errorf("INVALID_JSON:%w", err)
			}
			if end.(json.Delim) != ']' {
				return nil, errors.New("INVALID_JSON: expected ']'")
			}
			return arr, nil
		}
		return nil, errors.New("INVALID_JSON: unexpected delimiter")
	case json.Number:
		// Reject floats by requiring an integer representation.
		if bytes.ContainsAny([]byte(t.String()), ".eE") {
			return nil, errors.New("FLOAT_NOT_ALLOWED")
		}
		i, err := t.Int64()
		if err != nil {
			return nil, errors.New("INVALID_INT")
		}
		// Safe integer range for cross-language stability
		if float64(i) < SAFE_INT_MIN || float64(i) > SAFE_INT_MAX || math.Abs(float64(i)) > SAFE_INT_MAX {
			return nil, errors.New("INT_OUT_OF_RANGE")
		}
		return i, nil
	case string:
		return t, nil
	case bool:
		return t, nil
	case nil:
		return nil, nil
	default:
		return nil, errors.New("INVALID_JSON: unexpected token type")
	}
}

func normalize(v Value) (Value, error) {
	switch x := v.(type) {
	case map[string]Value:
		keys := make([]string, 0, len(x))
		for k := range x {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		out := make(map[string]Value, len(x))
		for _, k := range keys {
			nv, err := normalize(x[k])
			if err != nil {
				return nil, err
			}
			out[k] = nv
		}
		return out, nil
	case []Value:
		out := make([]Value, 0, len(x))
		for _, item := range x {
			nv, err := normalize(item)
			if err != nil {
				return nil, err
			}
			out = append(out, nv)
		}
		return out, nil
	case int64:
		return x, nil
	case string, bool, nil:
		return x, nil
	default:
		// No floats should exist in parsed output; treat as error.
		return nil, errors.New("FLOAT_NOT_ALLOWED")
	}
}

func canonicalJSON(v Value) (string, error) {
	nv, err := normalize(v)
	if err != nil {
		return "", err
	}
	b, err := json.Marshal(nv)
	if err != nil {
		return "", err
	}
	// json.Marshal emits no insignificant whitespace by default.
	return string(b), nil
}

func sha3_512_b64(data []byte) string {
	h := sha3.Sum512(data)
	return base64.StdEncoding.EncodeToString(h[:])
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("usage: json_canon_v1 <json-string>")
		os.Exit(2)
	}
	val, err := parseJSONStrictNoFloats([]byte(os.Args[1]))
	if err != nil {
		fmt.Println("error:", err)
		os.Exit(1)
	}
	canon, err := canonicalJSON(val)
	if err != nil {
		fmt.Println("error:", err)
		os.Exit(1)
	}
	fmt.Println(canon)
	fmt.Println(sha3_512_b64([]byte(canon)))
}
