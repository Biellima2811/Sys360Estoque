package com.sys360.api.modelo;

import jakarta.persistence.*;

import java.util.UUID;
@Entity
@Table(name = "tb_produto")
public class Produto {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private String nome;

    private double preco;
    private int quantidadeEstoque;

    // Relacionamento: Muitos produtos pertencem a Uma Categoria especifica.
    @ManyToOne
    @JoinColumn(name = "categoria_id")
    private Categoria categoria;

    public Produto() {
    }

    public Produto(UUID id, String nome, double preco, int quantidadeEstoque, Categoria categoria) {
        this.id = id;
        this.nome = nome;
        this.preco = preco;
        this.quantidadeEstoque = quantidadeEstoque;
        this.categoria = categoria;
    }

    // Regra de negocio: Adiciona item ao estoque
    public void adicionarEstoque(int quantidade){
        if (quantidade <= 0)
            throw new IllegalArgumentException("Quantidade deve ser um valor positivo");
        this.quantidadeEstoque += quantidade;
    }

    // Regra de negocio: Remover item no estoque
    public void removerEstoque(int quantidade){
        if (quantidade > this.quantidadeEstoque)
            throw new IllegalArgumentException("Estoque insuficiente");
        this.quantidadeEstoque -= quantidade;
    }

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public int getQuantidadeEstoque() {
        return quantidadeEstoque;
    }

    public void setQuantidadeEstoque(int quantidadeEstoque) {
        this.quantidadeEstoque = quantidadeEstoque;
    }

    public Categoria getCategoria() {
        return categoria;
    }

    public void setCategoria(Categoria categoria) {
        this.categoria = categoria;
    }
}
