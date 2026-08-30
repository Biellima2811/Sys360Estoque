import com.sys360.modelo.Produto;
import com.sys360.modelo.Categoria;

public class Main {
    static void main(String[] args) {
        Categoria catEletonicos = new Categoria("1", "Eletrônicos");
        Produto notebook = new Produto("10", "Notebook Aspire", 3500, 5, catEletonicos);
        System.out.println("Produto: " + notebook.getNome());
        System.out.println("Estoque incial: " + notebook.getQuantidadeEstoque());

        notebook.adicionarEstoque(10);
        System.out.println("Estoque após entrada: " + notebook.getQuantidadeEstoque() + " Produto: " + notebook.getNome());

        notebook.removerEstoque(3);
        System.out.println("Atualização de Estoque após saida: Item - " +  notebook.getNome() + " Quantidade: " +  notebook.getQuantidadeEstoque());

        System.out.println("Tentando venda acima do estoque atual....");
        try {
            notebook.removerEstoque(11);
            System.out.println("Atualização de Estoque: Produto - " +  notebook.getNome() +  " Quantidade: " +  notebook.getQuantidadeEstoque());
        } catch (IllegalArgumentException e) {
            System.out.println("ERRO - Operação bloqueada pelo sistema : " + e.getMessage());
        }
    }
}