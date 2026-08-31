package com.sys360.api.controller;

import com.sys360.api.modelo.Produto;
import com.sys360.api.repository.ProdutoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("api/produtos")
public class ProdutoController {
    @Autowired
    private ProdutoRepository repository;

    // Rota para criar o produto
    @PostMapping
    public Produto cadastrar(@RequestBody Produto produto){
        return repository.save(produto);
    }

    // Rota para listar os produtos
    @GetMapping
    public List<Produto> listar(){
        return repository.findAll();
    }

    // Rota para registrar ENTRADA de estoque
    @PutMapping("/{id}/entrada")
    public Produto resgistarEntrada(@PathVariable UUID id, @RequestParam int quantidade){
        // 1. Busca o produto no banco de dados pelo ID
        Produto produto = repository.findById(id)
                .orElseThrow(() -> new RuntimeException("Produto não encontrado!"));
        // 2. Regra de negocio da classe produto.
        produto.adicionarEstoque(quantidade);

        // 3. Salvar atualização no banco de dados.
        return repository.save(produto);
    }

    @PutMapping("/{id}/saida")
    public Produto resgistarSaida(@PathVariable UUID id, @RequestParam int quantidade){
        // 1. Buscar o produto no banco de dados pelo ID
        Produto produto = repository.findById(id)
                .orElseThrow(() -> new RuntimeException("Produto não encontrado!"));

        // 2. Regra de negocio para saida do produto.
        produto.removerEstoque(quantidade);

        // 3. Salva informação no banco de dados
        return repository.save(produto);
    }
}
