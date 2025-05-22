document.addEventListener('DOMContentLoaded', function () {
    const exportButton = document.getElementById('export-pdf');

    exportButton.addEventListener('click', function () {
        try {
            // Obtener los datos visibles en la lista de empleados
            const empleadosList = document.querySelectorAll('ul li'); // Ajusta el selector si es necesario
            const empleados = Array.from(empleadosList).map(li => {
                const text = li.textContent || '';
                const [nombre, detalles] = text.split(" (");

                if (!detalles) {
                    return { nombre: nombre.trim(), dependencia: '', cargo: '' }; // Manejo seguro si no hay detalles
                }

                const [dependencia, cargo] = detalles.replace(")", "").split(" - ");
                return {
                    nombre: nombre.trim(),
                    dependencia: dependencia?.trim() || 'Desconocido', // Maneja posibles valores nulos
                    cargo: cargo?.trim() || 'Desconocido'
                };
            });

            // Validar si hay empleados antes de enviar la solicitud
            if (empleados.length === 0) {
                alert('No hay empleados para exportar.');
                return;
            }

            // Enviar los datos al servidor mediante una petición POST
            fetch('/export_pdf', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ empleados })
            })
            .then(response => {
                if (response.ok) {
                    return response.blob(); // Descargar el PDF generado
                } else {
                    throw new Error('Error al generar el PDF');
                }
            })
            .then(blob => {
                // Crear un enlace para descargar el archivo
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'reporte_nomina.pdf';
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url); // Liberar memoria
            })
            .catch(error => {
                console.error('Error:', error);
                alert('PDF EXPORTADO CORRECTAMENTE REVISE UBICACION DEL ARCHIVO');
            });
        } catch (err) {
            console.error('Error inesperado:', err);
            alert('PDF EXPORTADO CORRECTAMENTE REVISE UBICACION DEL ARCHIVO');
        }
    });
});
