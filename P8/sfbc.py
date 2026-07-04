import numpy as np

def sfbc_encode(symbols): # Aquí se recibe lo símbolos en formato symb = [x1, x2, x3, x4, ...]

    # asegurar número par ya que el esquema Alamouti requiere pares de símbolos
    if len(symbols) % 2 != 0: #Si el número de símbolos es impar, se agrega un símbolo nulo (0) al final
        symbols = np.append(symbols, 0)

    #A continuación se separa por pares de símbolos, s1 y s2, y se crean dos secuencias de transmisión tx1 y tx2 según el esquema Alamouti.
    s1 = symbols[0::2]
    s2 = symbols[1::2]

    #Aquí se costruye la secuencia de transmisión tx1 y tx2.
    tx1 = np.zeros(len(symbols), dtype=complex)
    tx2 = np.zeros(len(symbols), dtype=complex)

    # Primera antena,
    tx1[0::2] = s1 #se añade los simbolos en posiciones pares. tx1 = [A 0 C 0 E 0]
    tx1[1::2] = -np.conj(s2) #añade simbolos conjugados negativos en posiciones impares. tx1 = [A -B* C -D* E -F*]

    tx2[0::2] = s2 #misma lógica que tx1, pero con los símbolos de s2. tx2 = [B 0 D 0 F 0]
    tx2[1::2] = np.conj(s1) #se agrega el conjugado de los símbolos de s1 en posiciones impares. tx2 = [B A* D C* F E*]

    return tx1, tx2