---
applyTo: "**/*.{clj,cljs,cljc,bb,edn.mdx?}"
description: "Clojure coding patterns and namespace handling"
---

# Clojure Quick Reference

## Namespace Structure

```clojure
(ns my-app.core
  (:require [clojure.string :as str]
            [clojure.set :as set]))
```

## Data Structures

```clojure
;; Vectors
[1 2 3]

;; Maps
{:name "Alice" :age 30}

;; Sets
#{1 2 3}

;; Keywords for keys
(:name person)  ; => "Alice"
```

## Functions

```clojure
(defn greet
  "Greet a person by name."
  [name]
  (str "Hello, " name "!"))

;; Anonymous
(fn [x] (* x 2))
#(* % 2)  ; shorthand
```

## Threading Macros

```clojure
;; Thread first (->)
(-> person :address :city)

;; Thread last (->>)
(->> numbers (filter even?) (map inc))
```

## Error Handling

```clojure
(try
  (risky-operation)
  (catch Exception e
    (log/error e "Operation failed")))
```

## Testing

```clojure
(deftest my-test
  (testing "addition"
    (is (= 4 (+ 2 2)))))
```

## Full Reference
See `.github/instructions/archive/clojure-full.md`
