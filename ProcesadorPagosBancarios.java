public class ProcesadorPagosBancarios {

    // Límite máximo permitido por transacción individual (ej. 500 millones MXN)
    private static final int MAX_TRANSACCION_INDIVIDUAL = 500_000_000;

    /**
     * Suma los montos de un lote de transferencias para validar contra el límite del día.
     * La lógica parece robusta porque valida cada transacción individualmente.
     */
    public int calcularTotalLote(int[] transferencias) {
        int sumaTotal = 0;

        for (int monto : transferencias) {
            // Validación de seguridad de negocio
            if (monto > 0 && monto <= MAX_TRANSACCION_INDIVIDUAL) {
                // Aquí ocurre el desbordamiento silencioso si el lote es grande.
                // Sonar y CodeQL ven una suma aritmética estándar.
                sumaTotal += monto;
            }
        }
        return sumaTotal;
    }

    /**
     * Propiedad para que JBMC verifique.
     * Queremos asegurar que la suma de valores positivos NUNCA sea menor que
     * uno de sus componentes (lo cual indicaría un desbordamiento).
     */
    public void verificarIntegridadSaldos(int t1, int t2, int t3, int t4, int t5) {
        int[] lote = {t1, t2, t3, t4, t5};
        int resultado = calcularTotalLote(lote);

        // Si todos los montos son positivos y válidos, el resultado debería ser >= t1
        // JBMC encontrará que con 5 transferencias de 500M, el total "da la vuelta".
        if (t1 > 0 && t2 > 0 && t3 > 0 && t4 > 0 && t5 > 0 &&
            t1 <= MAX_TRANSACCION_INDIVIDUAL && t2 <= MAX_TRANSACCION_INDIVIDUAL) {
            
            assert resultado >= t1;
        }
    }
}